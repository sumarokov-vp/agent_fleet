from datetime import UTC, datetime
from decimal import Decimal
from uuid import UUID

import psycopg
from psycopg.rows import class_row

from src.bounded_context.claude_service.entities.session import Session


class SessionRepo:
    def __init__(self, database_url: str) -> None:
        self._database_url = database_url

    def create(self, session: Session) -> None:
        with psycopg.connect(self._database_url) as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO sessions (
                        id, job_id, claude_session_id, started_at,
                        input_tokens, output_tokens, cost_usd
                    )
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                    """,
                    (
                        str(session.id),
                        str(session.job_id),
                        session.claude_session_id,
                        session.started_at,
                        session.input_tokens,
                        session.output_tokens,
                        session.cost_usd,
                    ),
                )
                conn.commit()

    def get_by_id(self, session_id: UUID) -> Session | None:
        with psycopg.connect(self._database_url) as conn:
            with conn.cursor(row_factory=class_row(Session)) as cur:
                cur.execute(
                    """
                    SELECT
                        id, job_id, claude_session_id, started_at, ended_at,
                        input_tokens, output_tokens, cost_usd
                    FROM sessions WHERE id = %s
                    """,
                    (str(session_id),),
                )
                return cur.fetchone()

    def update_metrics(
        self,
        session_id: UUID,
        claude_session_id: str,
        input_tokens: int,
        output_tokens: int,
        cost_usd: Decimal,
    ) -> None:
        with psycopg.connect(self._database_url) as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    UPDATE sessions SET
                        claude_session_id = %s,
                        ended_at = %s,
                        input_tokens = %s,
                        output_tokens = %s,
                        cost_usd = %s
                    WHERE id = %s
                    """,
                    (
                        claude_session_id,
                        datetime.now(tz=UTC),
                        input_tokens,
                        output_tokens,
                        cost_usd,
                        str(session_id),
                    ),
                )
                conn.commit()
