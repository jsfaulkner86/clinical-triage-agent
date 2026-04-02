# Clinical Triage Agent

> **LangGraph + Pydantic AI** — Epic In-Basket triage logic rebuilt as a stateful, auditable agentic system

[![Python](https://img.shields.io/badge/Python-3776AB?style=flat-square&logo=python&logoColor=white)]()
[![LangGraph](https://img.shields.io/badge/LangGraph-FF6B35?style=flat-square)]()
[![Pydantic](https://img.shields.io/badge/Pydantic-E92063?style=flat-square&logo=pydantic&logoColor=white)]()
[![Epic EHR](https://img.shields.io/badge/Epic-EHR-red?style=flat-square)]()

Built by [The Faulkner Group](https://thefaulknergroupadvisors.com) — directly informed by In-Basket workflow design across 12 Epic enterprise health systems.

---

## Problem Statement

Epic In-Basket is one of the most overloaded workflows in ambulatory care. Nurses and MAs spend hours manually triaging messages that follow predictable classification patterns — urgency assessment, message categorization, routing, documentation verification, and response drafting. This agent models that complete triage logic as a stateful, auditable LangGraph pipeline with HIPAA-compliant event logging on every decision.

---

## System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                       Patient Message Input                      │
│          (Epic In-Basket / FHIR Communication resource)           │
└───────────────────────────────┬─────────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────────┐
│                  LangGraph Triage State Machine                   │
│                                                                   │
│  [parse_intake] ──▶ [classify_acuity] ──▶ [route_to_pathway]    │
│       │                    │                       │             │
│  validation           acuity level             pathway +          │
│  check                assigned                 role assigned      │
│       │                    │                       │             │
│       ▼                    ▼                       ▼             │
│  [human_review] ◄── (>2 doc gaps)  ◄── [detect_documentation_gaps] │
│  (if flagged)                                       │             │
│                                                     ▼             │
│                                           [finalize_audit]        │
│                                                     │             │
│                                                     ▼             │
│                                        Routing Decision +         │
│                                        Audit Event Written        │
└─────────────────────────────────────────────────────────────────┘
          │ Append-only HIPAA audit log on every node transition
          ▼
┌─────────────────────────────────────────────────────────────────┐
│  PostgreSQL: triage_audit_log (append-only)                       │
└─────────────────────────────────────────────────────────────────┘
```

### Core Design Principles

- **Every triage decision is audited** — 10 distinct event types capture the full lifecycle from message receipt to routing completion.
- **Human review flags are non-negotiable** — >2 documentation gaps or validation failures set `requires_human_review = True`, matching the MA escalation threshold in Epic workflow governance.
- **Pydantic validation is enforced at every node** — typed schemas prevent silent data corruption across the state machine.
- **HIPAA posture** — `patient_id` fields are designed for de-identified tokens in non-PHI environments. Enable Presidio scrubbing before connecting to live Epic FHIR endpoints.

---

## Repository Structure

```
clinical-triage-agent/
├── app.py                          # Streamlit or FastAPI interface layer
├── main.py                         # Agent entry point — LangGraph graph definition
├── requirements.txt
│
├── audit/
│   ├── models.py                   # TriageAuditEvent Pydantic model (10 event types)
│   ├── logger.py                   # Append-only asyncpg writer — never raises
│   ├── queries.py                  # Read-side analytics: acuity distribution, gap summary
│   └── migrations/
│       └── 001_create_triage_audit_log.sql
│
└── tests/
    └── test_audit.py
```

---

## Technology Stack

| Layer | Technology | Rationale |
|---|---|---|
| **Agent Orchestration** | LangGraph | Stateful graph — each node maps to a discrete triage decision point |
| **Data Validation** | Pydantic AI | Typed schemas enforce completeness at every node transition |
| **LLM** | OpenAI GPT-4o | Classification + response drafting with structured output |
| **Audit Store** | PostgreSQL + asyncpg | Append-only HIPAA audit log — no ORM overhead on write path |
| **Language** | Python 3.11+ | Type hints throughout; async-native |

---

## Epic In-Basket Workflow Context

This agent models the real governance logic behind Epic In-Basket triage — the most overloaded workflow in ambulatory care. In production Epic environments, In-Basket message routing follows a strict taxonomy and escalation hierarchy that this agent replicates as a stateful LangGraph pipeline.

### Message Type Taxonomy

| Message Type | Default Route | Escalation Trigger |
|---|---|---|
| Clinical Advice Request | RN Pool | Symptom severity → provider |
| Rx Refill Request | MA Pool | Controlled substance → provider |
| Test Result Notification | Ordering Provider | Critical value → immediate |
| Scheduling Request | Front Desk | Urgent complaint → clinical |
| Administrative | Front Desk | None |

### Acuity-to-Pathway Mapping

| Acuity Level | Care Pathway | SLA |
|---|---|---|
| `EMERGENT` | Emergency Department — immediate physician notification | Immediate |
| `URGENT` | Acute Care — nurse assessment | Within 30 min |
| `SEMI-URGENT` | Same-Day Scheduled — provider queue | Within 4 hrs |
| `NON-URGENT` | Routine Scheduled — next available | Within 72 hrs |
| `ADMINISTRATIVE` | Front Desk — non-clinical resolution | Standard |

### Documentation Governance

The agent enforces the same 5-field completeness check required before Epic In-Basket routing closes:

- Vital signs documented
- Allergy status confirmed
- Medication reconciliation complete
- Reason for visit documented
- Insurance verification status

> More than 2 missing fields triggers `requires_human_review = True` — matching the MA escalation threshold in Epic workflow governance.

---

## Audit Event Lifecycle

```
message_received
    └── intake_parsed | intake_validation_failed
            └── acuity_classified
                    └── pathway_assigned
                            └── documentation_gap_detected (0–n)
                                    └── human_review_flagged (if gaps > 2)
                                    └── response_drafted
                                            └── routing_completed | routing_failed
```

---

## Epic FHIR Production Integration Path

| Integration Point | FHIR Resource | Epic API |
|---|---|---|
| Inbound patient messages | `Communication` | MyChart Messaging API |
| Work item routing | `Task` | In-Basket Task API |
| Patient demographics | `Patient` | R4 Patient resource |
| Encounter context | `Encounter` | R4 Encounter resource |
| Allergy verification | `AllergyIntolerance` | R4 AllergyIntolerance |

**Auth:** SMART-on-FHIR Backend Services (system-to-system, no user login required)
**Sandbox:** [Epic on FHIR Sandbox](https://fhir.epic.com) — free registration, full R4 resource access
**App Registration:** Non-Patient-Facing Application registration via Epic’s vendor portal

---

## Compliance Posture

- **HIPAA:** `triage_audit_log` is an append-only table — satisfies audit log requirements for covered entities. `patient_id` stored as de-identified token by default. Connect live PHI only through an Epic SMART-on-FHIR integration with BAA in place.
- **Change Management:** Before connecting to a production Epic environment, this agent requires IS governance review, CMIO sign-off, and CAB approval for any workflow that touches In-Basket routing.
- **Escalation Safety Net:** `requires_human_review = True` is a hard flag — the agent never silently routes high-acuity or documentation-incomplete messages without surfacing them for clinical review.

---

## Known Failure Modes

| Failure Mode | Impact | Mitigation |
|---|---|---|
| LLM mis-classifies EMERGENT as URGENT | Delayed escalation | Confidence threshold + mandatory human review below 0.90 for EMERGENT acuity |
| Epic API rate limiting | Message ingestion lag | Exponential backoff + queue depth monitoring |
| Documentation gap check on incomplete patient record | False-positive human review flags | Validate FHIR resource completeness before gap check runs |
| FHIR token expiration during long triage session | Silent auth failure | Refresh token logic with 5-min pre-expiry rotation |

---

## Local Development

```bash
git clone https://github.com/jsfaulkner86/clinical-triage-agent
cd clinical-triage-agent
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env

# Run database migration
psql $DATABASE_URL -f audit/migrations/001_create_triage_audit_log.sql

# Start agent
python main.py

# Run tests
pytest tests/ -v
```

---

## What's Next

- Epic MyChart message ingestion via FHIR `Communication` resource
- Escalation agent for EMERGENT and URGENT acuity paths
- Clinician feedback loop for response draft quality scoring
- Integration with `ehr-mcp` interoperability protocol

---

*Part of The Faulkner Group's healthcare agentic AI portfolio. See all projects at [github.com/jsfaulkner86](https://github.com/jsfaulkner86)*
