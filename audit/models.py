"""Audit event models for the Clinical Triage Agent."""
import uuid
from datetime import datetime
from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field


class TriageAuditEventType(str, Enum):
    MESSAGE_RECEIVED = "message_received"
    INTAKE_PARSED = "intake_parsed"
    INTAKE_VALIDATION_FAILED = "intake_validation_failed"
    ACUITY_CLASSIFIED = "acuity_classified"
    PATHWAY_ASSIGNED = "pathway_assigned"
    DOCUMENTATION_GAP_DETECTED = "documentation_gap_detected"
    HUMAN_REVIEW_FLAGGED = "human_review_flagged"
    RESPONSE_DRAFTED = "response_drafted"
    ROUTING_COMPLETED = "routing_completed"
    ROUTING_FAILED = "routing_failed"


class TriageAuditEvent(BaseModel):
    """Immutable audit record for a single triage decision event."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    created_at: datetime = Field(default_factory=datetime.utcnow)
    event_type: TriageAuditEventType
    patient_id: Optional[str] = None         # de-identified in non-PHI environments
    message_id: Optional[str] = None
    thread_id: Optional[str] = None          # LangGraph thread
    acuity_level: Optional[str] = None       # EMERGENT | URGENT | SEMI-URGENT | NON-URGENT | ADMINISTRATIVE
    message_type: Optional[str] = None
    assigned_pathway: Optional[str] = None
    assigned_role: Optional[str] = None
    documentation_gaps: Optional[list[str]] = None
    requires_human_review: bool = False
    confidence: Optional[float] = None
    error_detail: Optional[str] = None
    metadata: Optional[dict] = None


AUDIT_TABLE_DDL = """
CREATE TABLE IF NOT EXISTS triage_audit_log (
    id                      UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    created_at              TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    event_type              TEXT NOT NULL,
    patient_id              TEXT,
    message_id              TEXT,
    thread_id               TEXT,
    acuity_level            TEXT,
    message_type            TEXT,
    assigned_pathway        TEXT,
    assigned_role           TEXT,
    documentation_gaps      TEXT[],
    requires_human_review   BOOLEAN NOT NULL DEFAULT FALSE,
    confidence              NUMERIC(5,4),
    error_detail            TEXT,
    metadata                JSONB
);

CREATE INDEX IF NOT EXISTS idx_triage_audit_event_type    ON triage_audit_log (event_type);
CREATE INDEX IF NOT EXISTS idx_triage_audit_patient       ON triage_audit_log (patient_id);
CREATE INDEX IF NOT EXISTS idx_triage_audit_acuity        ON triage_audit_log (acuity_level);
CREATE INDEX IF NOT EXISTS idx_triage_audit_created_at    ON triage_audit_log (created_at DESC);
CREATE INDEX IF NOT EXISTS idx_triage_audit_human_review  ON triage_audit_log (requires_human_review);

COMMENT ON TABLE triage_audit_log IS
    'Immutable append-only audit trail for all clinical triage decisions. HIPAA audit log — never UPDATE or DELETE rows.';
"""
