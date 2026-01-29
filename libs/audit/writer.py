import json
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any

from libs.core.context import request_id_ctx, trace_id_ctx
from libs.risk.audit.hasher import hash_payload
from libs.risk.decisioning.types import RiskDecision


@dataclass(frozen=True)
class AuditWriteResult:
    audit_id: str


class AuditWriter:
    def write(self, decision: RiskDecision, raw_input: dict[str, Any]) -> AuditWriteResult:
        raise NotImplementedError


_POSTGRES_DDL = """
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
"""


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


def _pick_actor(raw_input: dict[str, Any]) -> str | None:
    t = raw_input.get("text") or {}
    return t.get("customer_id") if isinstance(t, dict) else None


def _pick_entity(raw_input: dict[str, Any]) -> tuple[str | None, str | None]:
    t = raw_input.get("text") or {}
    if isinstance(t, dict) and t.get("case_id"):
        return ("text_case", str(t.get("case_id")))
    f = raw_input.get("fraud")
    if isinstance(f, dict):
        return ("transaction", None)
    return (None, None)


def _extract_model_prompt_versions(decision: RiskDecision) -> tuple[str | None, str | None, str | None]:
    p = decision.provenance
    return (p.model_name, p.model_version, p.prompt_version)


_INSERT_SQL = """
INSERT INTO audit.audit_event (
  created_at,
  event_type, env, service_name,
  request_id, trace_id,
  actor, entity_type, entity_id,
  model_name, model_version, prompt_version,
  risk_category, risk_score,
  reason_codes, evidence,
  input_hash, payload
) VALUES (
  %(created_at)s,
  %(event_type)s, %(env)s, %(service_name)s,
  %(request_id)s, %(trace_id)s,
  %(actor)s, %(entity_type)s, %(entity_id)s,
  %(model_name)s, %(model_version)s, %(prompt_version)s,
  %(risk_category)s, %(risk_score)s,
  %(reason_codes)s::jsonb, %(evidence)s::jsonb,
  %(input_hash)s, %(payload)s::jsonb
)
RETURNING id
"""


class PostgresAuditWriter(AuditWriter):
    def __init__(self, dsn: str, env: str = "dev", service_name: str = "risk_api"):
        try:
            import psycopg
        except Exception as e:
            raise RuntimeError("psycopg is required for PostgresAuditWriter") from e

        self._psycopg = psycopg
        self._dsn = dsn
        self.env = env
        self.service_name = service_name
        self._ensure_schema()

    def _connect(self):
        return self._psycopg.connect(self._dsn)

    def _ensure_schema(self) -> None:
        with self._connect() as conn:
            with conn.cursor() as cur:
                cur.execute(_POSTGRES_DDL)
            conn.commit()

    def write(self, decision: RiskDecision, raw_input: dict[str, Any]) -> AuditWriteResult:
        created_at = _utcnow()
        rid = request_id_ctx.get()
        tid = trace_id_ctx.get()

        actor = _pick_actor(raw_input)
        entity_type, entity_id = _pick_entity(raw_input)
        model_name, model_version, prompt_version = _extract_model_prompt_versions(decision)

        input_hash = hash_payload(raw_input)

        payload = {
            "decision": decision.model_dump(),
            "raw_input": raw_input,
            "meta": {"request_id": rid, "trace_id": tid},
        }

        row = {
            "created_at": created_at,
            "event_type": "risk_decision",
            "env": self.env,
            "service_name": self.service_name,
            "request_id": rid,
            "trace_id": tid,
            "actor": actor,
            "entity_type": entity_type,
            "entity_id": entity_id,
            "model_name": model_name,
            "model_version": model_version,
            "prompt_version": prompt_version,
            "risk_category": str(decision.risk_category),
            "risk_score": float(decision.risk_score),
            "reason_codes": json.dumps([r.value for r in decision.reasons]),
            "evidence": json.dumps([e.model_dump() for e in decision.evidence]),
            "input_hash": input_hash,
            "payload": json.dumps(payload),
        }

        with self._connect() as conn:
            with conn.cursor() as cur:
                cur.execute(_INSERT_SQL, row)
                audit_id = str(cur.fetchone()[0])
            conn.commit()

        return AuditWriteResult(audit_id=audit_id)