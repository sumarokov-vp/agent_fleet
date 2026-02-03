import json
import logging
from datetime import UTC, datetime
from decimal import Decimal
from typing import Any
from uuid import UUID, uuid4

import redis
from claude_code_sdk import AssistantMessage, ResultMessage, TextBlock, ToolUseBlock

from src.bounded_context.agent_control.services.agent_session_manager import (
    AgentSessionManager,
)
from src.bounded_context.claude_service.entities.job import JobStatus
from src.bounded_context.claude_service.entities.session import Session
from src.bounded_context.claude_service.repos.job_repo import JobRepo
from src.bounded_context.claude_service.repos.session_repo import SessionRepo
from src.messaging import (
    ClaudeRequest,
    ClaudeResponse,
    MessageConsumer,
    MessagePublisher,
)
from src.messaging.connection import RabbitMQConnection

logger = logging.getLogger(__name__)


class ClaudeRequestConsumer(MessageConsumer[ClaudeRequest]):
    SESSION_STORAGE_KEY_PREFIX = "agent_fleet:job_session:"
    SESSION_TTL_SECONDS = 3600

    def __init__(
        self,
        connection: RabbitMQConnection,
        session_manager: AgentSessionManager,
        response_publisher: MessagePublisher,
        job_repo: JobRepo,
        session_repo: SessionRepo,
        redis_url: str,
    ) -> None:
        super().__init__(
            connection=connection,
            exchange_name="claude.requests",
            queue_name="claude.requests",
            routing_key="claude.request",
            prefetch_count=5,
        )
        self._session_manager = session_manager
        self._response_publisher = response_publisher
        self._job_repo = job_repo
        self._session_repo = session_repo
        self._redis = redis.from_url(redis_url)  # pyright: ignore[reportUnknownMemberType]

    def _parse_message(self, body: bytes) -> ClaudeRequest:
        return ClaudeRequest.model_validate_json(body)

    async def _handle_message(self, message: ClaudeRequest) -> None:
        logger.info(
            "Processing request %s for user %s (project: %s, mode: %s)",
            message.request_id,
            message.user_id,
            message.project_id,
            message.permission_mode,
        )
        await self._execute_request(message)

    async def _execute_request(self, request: ClaudeRequest) -> None:
        agent_session = None
        db_session_id = uuid4()

        try:
            db_session = Session(
                id=db_session_id,
                job_id=request.job_id or uuid4(),
                started_at=datetime.now(tz=UTC),
            )
            self._session_repo.create(db_session)

            if request.job_id:
                self._job_repo.update_status(request.job_id, JobStatus.RUNNING)

            agent_session = self._session_manager.create_session(
                project_id=request.project_id,
                working_directory=request.project_path,
                permission_mode=request.permission_mode,
                resume_session_id=request.session_id,
            )

            client = self._session_manager.get_client(agent_session.id)
            if not client:
                await self._publish_error(request, "Failed to create client session")
                return

            await client.connect()

            prompt = request.prompt
            if request.answer_to_question:
                prompt = self._format_answer(request.answer_to_question)

            await client.query(prompt)

            accumulated_text: list[str] = []
            result_message: ResultMessage | None = None

            async for msg in client.receive_messages():
                if isinstance(msg, ResultMessage):
                    result_message = msg
                    break
                if isinstance(msg, AssistantMessage):
                    for block in msg.content:
                        if isinstance(block, ToolUseBlock):
                            if block.name == "AskUserQuestion":
                                await self._handle_ask_question(
                                    request=request,
                                    session_id=agent_session.id,
                                    questions=block.input.get("questions", []),  # pyright: ignore[reportUnknownMemberType]
                                )
                                self._save_job_session(agent_session.id, request.job_id)
                                self._update_session_metrics(
                                    db_session_id=db_session_id,
                                    claude_session_id=agent_session.id,
                                    job_id=request.job_id,
                                    result=result_message,
                                )
                                return

                            if block.name == "ExitPlanMode":
                                await self._handle_plan_ready(
                                    request=request,
                                    session_id=agent_session.id,
                                    plan_content=block.input.get("plan"),  # pyright: ignore[reportUnknownMemberType]
                                    accumulated_text="\n".join(accumulated_text),
                                )
                                self._save_job_session(agent_session.id, request.job_id)
                                self._update_session_metrics(
                                    db_session_id=db_session_id,
                                    claude_session_id=agent_session.id,
                                    job_id=request.job_id,
                                    result=result_message,
                                )
                                return

                        elif isinstance(block, TextBlock):
                            if request.permission_mode == "plan":
                                accumulated_text.append(block.text)
                            else:
                                await self._publish_text(request, block.text)

            self._update_session_metrics(
                db_session_id=db_session_id,
                claude_session_id=agent_session.id,
                job_id=request.job_id,
                result=result_message,
            )

            if request.job_id:
                self._job_repo.update_status(request.job_id, JobStatus.COMPLETED)

            await self._publish_completed(request, agent_session.id)

        except Exception as e:
            logger.exception("Error executing request %s", request.request_id)
            if request.job_id:
                self._job_repo.update_status(request.job_id, JobStatus.FAILED)
            await self._publish_error(request, str(e))
        finally:
            if agent_session:
                await self._session_manager.close_session(agent_session.id)

    def _format_answer(self, answer: dict[str, str]) -> str:
        parts = []
        for question_id, answer_text in answer.items():
            parts.append(f"{question_id}: {answer_text}")
        return "\n".join(parts)

    def _update_session_metrics(
        self,
        db_session_id: UUID,
        claude_session_id: str,
        job_id: UUID | None,
        result: ResultMessage | None,
    ) -> None:
        if result is None:
            return

        input_tokens, output_tokens, cost_usd = self._extract_metrics(result)

        self._session_repo.update_metrics(
            session_id=db_session_id,
            claude_session_id=claude_session_id,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            cost_usd=cost_usd,
        )

        if job_id:
            self._job_repo.increment_metrics(
                job_id=job_id,
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                cost_usd=cost_usd,
            )

    def _extract_metrics(self, result: ResultMessage) -> tuple[int, int, Decimal]:
        usage = result.usage or {}
        input_tokens = (
            usage.get("input_tokens", 0)
            + usage.get("cache_creation_input_tokens", 0)
            + usage.get("cache_read_input_tokens", 0)
        )
        output_tokens = usage.get("output_tokens", 0)
        cost_usd = Decimal(str(result.total_cost_usd or 0))
        return input_tokens, output_tokens, cost_usd

    async def _handle_ask_question(
        self,
        request: ClaudeRequest,
        session_id: str,
        questions: list[dict[str, Any]],
    ) -> None:
        response = ClaudeResponse(
            request_id=request.request_id,
            client_type=request.client_type,
            user_id=request.user_id,
            response_type="ask_question",
            questions=questions,
            session_id=session_id,
            timestamp=datetime.now(tz=UTC),
        )
        await self._response_publisher.publish(
            message=response,
            routing_key=f"response.{request.client_type}.ask_question",
        )

    async def _handle_plan_ready(
        self,
        request: ClaudeRequest,
        session_id: str,
        plan_content: str | None,
        accumulated_text: str,
    ) -> None:
        response = ClaudeResponse(
            request_id=request.request_id,
            client_type=request.client_type,
            user_id=request.user_id,
            response_type="plan_ready",
            plan_content=plan_content,
            accumulated_text=accumulated_text,
            session_id=session_id,
            timestamp=datetime.now(tz=UTC),
        )
        await self._response_publisher.publish(
            message=response,
            routing_key=f"response.{request.client_type}.plan_ready",
        )

    async def _publish_text(self, request: ClaudeRequest, text: str) -> None:
        response = ClaudeResponse(
            request_id=request.request_id,
            client_type=request.client_type,
            user_id=request.user_id,
            response_type="text",
            text=text,
            timestamp=datetime.now(tz=UTC),
        )
        await self._response_publisher.publish(
            message=response,
            routing_key=f"response.{request.client_type}.text",
        )

    async def _publish_completed(
        self, request: ClaudeRequest, session_id: str
    ) -> None:
        response = ClaudeResponse(
            request_id=request.request_id,
            client_type=request.client_type,
            user_id=request.user_id,
            response_type="completed",
            session_id=session_id,
            timestamp=datetime.now(tz=UTC),
        )
        await self._response_publisher.publish(
            message=response,
            routing_key=f"response.{request.client_type}.completed",
        )

    async def _publish_error(
        self, request: ClaudeRequest, error_message: str
    ) -> None:
        response = ClaudeResponse(
            request_id=request.request_id,
            client_type=request.client_type,
            user_id=request.user_id,
            response_type="error",
            error_message=error_message,
            timestamp=datetime.now(tz=UTC),
        )
        await self._response_publisher.publish(
            message=response,
            routing_key=f"response.{request.client_type}.error",
        )

    def _save_job_session(self, session_id: str, job_id: UUID | None) -> None:
        if job_id is None:
            return
        key = f"{self.SESSION_STORAGE_KEY_PREFIX}{session_id}"
        data = json.dumps({"job_id": str(job_id)})
        self._redis.set(key, data, ex=self.SESSION_TTL_SECONDS)
