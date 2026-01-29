CREATE SCHEMA IF NOT EXISTS audit;

CREATE TABLE IF NOT EXISTS audit.audit_event (
  id BIGSERIAL PRIMARY KEY,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

  event_type TEXT NOT NULL,
  env TEXT NOT NULL,
  service_name TEXT NOT NULL,

  request_id TEXT,
  trace_id TEXT,

  actor TEXT,

  entity_type TEXT,
  entity_id TEXT,

  model_name TEXT,
  model_version TEXT,
  prompt_version TEXT,

  risk_category TEXT,
  risk_score DOUBLE PRECISION,

  reason_codes JSONB,
  evidence JSONB,

  input_hash TEXT,

  payload JSONB NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_audit_event_created_at
  ON audit.audit_event (created_at);

CREATE INDEX IF NOT EXISTS idx_audit_event_entity
  ON audit.audit_event (entity_type, entity_id);

CREATE INDEX IF NOT EXISTS idx_audit_event_request_id
  ON audit.audit_event (request_id);

CREATE INDEX IF NOT EXISTS idx_audit_event_trace_id
  ON audit.audit_event (trace_id);

CREATE INDEX IF NOT EXISTS idx_audit_event_model
  ON audit.audit_event (model_name, model_version);