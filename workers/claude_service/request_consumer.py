import logging
from datetime import UTC, datetime
from typing import Any

import redis
from claude_code_sdk import AssistantMessage, TextBlock, ToolUseBlock

from src.bounded_context.agent_control.services.agent_session_manager import (
    AgentSessionManager,
)
from src.messaging import ClaudeRequest, ClaudeResponse, MessageConsumer, MessagePublisher
from src.messaging.connection import RabbitMQConnection

logger = logging.getLogger(__name__)


class ClaudeRequestConsumer(MessageConsumer[ClaudeRequest]):
    SESSION_STORAGE_KEY_PREFIX = "agent_fleet:claude_session:"
    SESSION_TTL_SECONDS = 3600

    def __init__(
        self,
        connection: RabbitMQConnection,
        session_manager: AgentSessionManager,
        response_publisher: MessagePublisher,
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
        self._redis = redis.from_url(redis_url)  # pyright: ignore[reportUnknownMemberType]

    def _parse_message(self, body: bytes) -> ClaudeRequest:
        return ClaudeRequest.model_validate_json(body)

    async def _handle_message(self, request: ClaudeRequest) -> None:
        logger.info(
            "Processing request %s for user %s (project: %s, mode: %s)",
            request.request_id,
            request.user_id,
            request.project_id,
            request.permission_mode,
        )
        await self._execute_request(request)

    async def _execute_request(self, request: ClaudeRequest) -> None:
        session = None
        try:
            session = self._session_manager.create_session(
                project_id=request.project_id,
                working_directory=request.project_path,
                permission_mode=request.permission_mode,
                resume_session_id=request.session_id,
            )

            client = self._session_manager.get_client(session.id)
            if not client:
                await self._publish_error(request, "Failed to create client session")
                return

            await client.connect()

            prompt = request.prompt
            if request.answer_to_question:
                prompt = self._format_answer(request.answer_to_question)

            await client.query(prompt)

            accumulated_text: list[str] = []

            async for msg in client.receive_messages():
                if isinstance(msg, AssistantMessage):
                    for block in msg.content:
                        if isinstance(block, ToolUseBlock):
                            if block.name == "AskUserQuestion":
                                await self._handle_ask_question(
                                    request=request,
                                    session_id=session.id,
                                    questions=block.input.get("questions", []),  # pyright: ignore[reportUnknownMemberType]
                                )
                                return

                            if block.name == "ExitPlanMode":
                                await self._handle_plan_ready(
                                    request=request,
                                    session_id=session.id,
                                    plan_content=block.input.get("plan"),  # pyright: ignore[reportUnknownMemberType]
                                    accumulated_text="\n".join(accumulated_text),
                                )
                                return

                        elif isinstance(block, TextBlock):
                            if request.permission_mode == "plan":
                                accumulated_text.append(block.text)
                            else:
                                await self._publish_text(request, block.text)

            await self._publish_completed(request, session.id)

        except Exception as e:
            logger.exception("Error executing request %s", request.request_id)
            await self._publish_error(request, str(e))
        finally:
            if session:
                await self._session_manager.close_session(session.id)

    def _format_answer(self, answer: dict[str, str]) -> str:
        parts = []
        for question_id, answer_text in answer.items():
            parts.append(f"{question_id}: {answer_text}")
        return "\n".join(parts)

    async def _handle_ask_question(
        self,
        request: ClaudeRequest,
        session_id: str,
        questions: list[dict[str, Any]],
    ) -> None:
        self._save_session_id(request.user_id, session_id)

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
        self._save_session_id(request.user_id, session_id)

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

    def _save_session_id(self, user_id: int, session_id: str) -> None:
        key = f"{self.SESSION_STORAGE_KEY_PREFIX}{user_id}"
        self._redis.set(key, session_id, ex=self.SESSION_TTL_SECONDS)

    def _get_session_id(self, user_id: int) -> str | None:
        key = f"{self.SESSION_STORAGE_KEY_PREFIX}{user_id}"
        value = self._redis.get(key)
        if value:
            return value.decode("utf-8")  # pyright: ignore[reportAttributeAccessIssue]
        return None
