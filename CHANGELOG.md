# Changelog

All notable changes to the Clinical Triage Agent are documented here.

Format: [Keep a Changelog](https://keepachangelog.com/en/1.0.0/)
Versioning: [Semantic Versioning](https://semver.org/)

---

## [1.0.0] — 2026-03-22

### Added
- LangGraph 6-node triage state machine
  - `parse_intake` — message validation and structured field extraction
  - `classify_acuity` — GPT-4o acuity classification (EMERGENT / URGENT / SEMI-URGENT / NON-URGENT / ADMINISTRATIVE) with confidence threshold
  - `route_to_pathway` — acuity-to-SLA pathway assignment
  - `detect_documentation_gaps` — 5-field Epic completeness check
  - `human_review` — hard flag when gaps > 2 or confidence < 0.90
  - `finalize_audit` — routing completion event
- Append-only `triage_audit_log` (PostgreSQL + asyncpg) — 10 distinct event types
- PydanticAI typed schemas at every node transition
- Acuity-to-pathway mapping aligned with Epic In-Basket governance (EMERGENT → ED immediate; URGENT → 30 min; SEMI-URGENT → 4h; NON-URGENT → 72h; ADMINISTRATIVE → standard)
- 5-field documentation completeness check: vitals, allergy status, medication reconciliation, reason for visit, insurance verification
- `requires_human_review = True` hard flag — never silent on high-acuity or incomplete documentation
- `audit/models.py` — TriageAuditEvent Pydantic model (10 event types)
- `audit/logger.py` — append-only asyncpg writer
- `audit/queries.py` — acuity distribution, documentation gap summary
- `audit/migrations/001_create_triage_audit_log.sql`
- Streamlit / FastAPI interface layer (`app.py`)
- CONTRIBUTING.md

---

## [Unreleased]

### Planned
- Epic MyChart message ingestion via FHIR `Communication` resource
- Escalation agent for EMERGENT and URGENT acuity paths
- Clinician feedback loop for response draft quality scoring
- HIPAA guardrail integration via `healthcare-compliance-guardrail`
- Live EHR context via `ehr-mcp`
- LangSmith tracing integration
