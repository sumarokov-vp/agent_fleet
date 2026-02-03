-- Rollback: Drop jobs and sessions tables

DROP INDEX IF EXISTS idx_sessions_job_id;
DROP INDEX IF EXISTS idx_jobs_status;
DROP INDEX IF EXISTS idx_jobs_project_id;

DROP TABLE IF EXISTS sessions;
DROP TABLE IF EXISTS jobs;
