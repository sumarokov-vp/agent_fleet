from datetime import UTC, datetime
from decimal import Decimal
from uuid import UUID

import psycopg
from psycopg.rows import class_row

from src.bounded_context.claude_service.entities.job import Job, JobStatus


class JobRepo:
    def __init__(self, database_url: str) -> None:
        self._database_url = database_url

    def create(self, job: Job) -> None:
        with psycopg.connect(self._database_url) as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO jobs (
                        id, external_task_id, project_id, status, created_at,
                        total_input_tokens, total_output_tokens,
                        total_cost_usd, total_sessions
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """,
                    (
                        str(job.id),
                        job.external_task_id,
                        job.project_id,
                        job.status.value,
                        job.created_at,
                        job.total_input_tokens,
                        job.total_output_tokens,
                        job.total_cost_usd,
                        job.total_sessions,
                    ),
                )
                conn.commit()

    def get_by_id(self, job_id: UUID) -> Job | None:
        with psycopg.connect(self._database_url) as conn:
            with conn.cursor(row_factory=class_row(Job)) as cur:
                cur.execute(
                    """
                    SELECT id, external_task_id, project_id, status,
                           created_at, completed_at, total_input_tokens,
                           total_output_tokens, total_cost_usd, total_sessions
                    FROM jobs WHERE id = %s
                    """,
                    (str(job_id),),
                )
                return cur.fetchone()

    def update_status(self, job_id: UUID, status: JobStatus) -> None:
        with psycopg.connect(self._database_url) as conn:
            with conn.cursor() as cur:
                if status in (JobStatus.COMPLETED, JobStatus.FAILED):
                    cur.execute(
                        "UPDATE jobs SET status = %s, completed_at = %s WHERE id = %s",
                        (status.value, datetime.now(tz=UTC), str(job_id)),
                    )
                else:
                    cur.execute(
                        "UPDATE jobs SET status = %s WHERE id = %s",
                        (status.value, str(job_id)),
                    )
                conn.commit()

    def increment_metrics(
        self,
        job_id: UUID,
        input_tokens: int,
        output_tokens: int,
        cost_usd: Decimal,
    ) -> None:
        with psycopg.connect(self._database_url) as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    UPDATE jobs SET
                        total_input_tokens = total_input_tokens + %s,
                        total_output_tokens = total_output_tokens + %s,
                        total_cost_usd = total_cost_usd + %s,
                        total_sessions = total_sessions + 1
                    WHERE id = %s
                    """,
                    (input_tokens, output_tokens, cost_usd, str(job_id)),
                )
                conn.commit()
