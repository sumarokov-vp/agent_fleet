-- Jobs table for tracking Claude Code task execution
-- depends:

CREATE TABLE jobs (
    id UUID PRIMARY KEY,
    external_task_id VARCHAR(255),
    project_id VARCHAR(255) NOT NULL,
    status VARCHAR(50) NOT NULL DEFAULT 'pending',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    completed_at TIMESTAMPTZ,
    total_input_tokens BIGINT DEFAULT 0,
    total_output_tokens BIGINT DEFAULT 0,
    total_cost_usd DECIMAL(10, 6) DEFAULT 0,
    total_sessions INTEGER DEFAULT 0,
    CHECK (status IN ('pending', 'running', 'completed', 'failed'))
);

CREATE TABLE sessions (
    id UUID PRIMARY KEY,
    job_id UUID NOT NULL REFERENCES jobs(id),
    claude_session_id VARCHAR(255),
    started_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    ended_at TIMESTAMPTZ,
    input_tokens BIGINT DEFAULT 0,
    output_tokens BIGINT DEFAULT 0,
    cost_usd DECIMAL(10, 6) DEFAULT 0
);

CREATE INDEX idx_jobs_project_id ON jobs(project_id);
CREATE INDEX idx_jobs_status ON jobs(status);
CREATE INDEX idx_sessions_job_id ON sessions(job_id);
