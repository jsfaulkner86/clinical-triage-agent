-- Migration: 001_create_triage_audit_log
-- Append-only HIPAA audit trail for clinical triage decisions.
-- Safe to re-run (IF NOT EXISTS guards).

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
    'Immutable append-only HIPAA audit trail for all clinical triage decisions. Never UPDATE or DELETE rows.';
