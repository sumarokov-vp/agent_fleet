import logging
from pathlib import Path
from typing import cast

import psycopg
from psycopg.sql import SQL

logger = logging.getLogger(__name__)


def apply_migrations(database_url: str) -> None:
    migrations_dir = Path(__file__).parent / "sql"

    with psycopg.connect(database_url) as conn:
        with conn.cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS _migrations (
                    id SERIAL PRIMARY KEY,
                    name VARCHAR(255) NOT NULL UNIQUE,
                    applied_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
                )
            """)
            conn.commit()

            cur.execute("SELECT name FROM _migrations ORDER BY name")
            applied = {row[0] for row in cur.fetchall()}

        migration_files = sorted(
            f
            for f in migrations_dir.glob("*.sql")
            if not f.name.endswith(".rollback.sql")
        )

        for migration_file in migration_files:
            migration_name = migration_file.stem

            if migration_name in applied:
                logger.debug("Migration %s already applied", migration_name)
                continue

            logger.info("Applying migration: %s", migration_name)

            sql_content = migration_file.read_text(encoding="utf-8")

            with conn.cursor() as cur:
                cur.execute(cast(SQL, sql_content))
                cur.execute(
                    "INSERT INTO _migrations (name) VALUES (%s)",
                    (migration_name,),
                )
                conn.commit()

            logger.info("Migration %s applied successfully", migration_name)
