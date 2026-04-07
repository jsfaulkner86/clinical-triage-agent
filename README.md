<div align="center">

<br />

# 🏥 Clinical Triage Agent

**Epic In-Basket is the most overloaded workflow in ambulatory care.**  
**Nurses and MAs spend hours triaging messages that follow completely predictable patterns.**  
**Urgency assessment. Categorization. Routing. Documentation check. Response draft.**  
**Every time. Manually.**

This agent models that complete triage logic as a **stateful, auditable LangGraph pipeline** —  
built directly from In-Basket workflow governance across 12 Epic enterprise health systems.

<br />

[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=flat-square&logo=python&logoColor=white)](https://python.org)
[![LangGraph](https://img.shields.io/badge/LangGraph-Stateful%20State%20Machine-FF6B35?style=flat-square)](https://langchain-ai.github.io/langgraph/)
[![PydanticAI](https://img.shields.io/badge/Pydantic%20AI-Typed%20Node%20Validation-E92063?style=flat-square&logo=pydantic&logoColor=white)](https://ai.pydantic.dev)
[![Epic](https://img.shields.io/badge/Epic-FHIR%20R4%20Integration%20Path-C8102E?style=flat-square)](https://fhir.epic.com)
[![HIPAA](https://img.shields.io/badge/HIPAA-Audit%20Compliant-0EA5E9?style=flat-square)]()
[![License](https://img.shields.io/badge/License-MIT-gray?style=flat-square)](LICENSE)

<br />

[Architecture](#system-architecture) · [Epic Workflow Context](#epic-in-basket-workflow-context) · [Acuity Mapping](#acuity-to-pathway-mapping) · [FHIR Integration](#epic-fhir-production-integration-path) · [Quick Start](#local-development)

<br />

</div>

---

## The Real Workflow

I've architected In-Basket governance across 12 enterprise Epic deployments. The manual triage workflow looked the same at all of them:

> Message arrives in In-Basket. MA opens it. Reads the chief complaint. Mentally runs through the acuity checklist. Checks the chart for documentation completeness. Decides the routing. Drafts a response or escalates. Closes the message. Opens the next one.

For a high-volume primary care practice, that's **300–600 messages per day**. Each one touched manually. Each one following the same decision logic that hasn't changed in a decade.

The logic is learnable. The routing rules are documented. The documentation governance checklist is a known finite set. This is exactly the class of workflow that agentic AI is built for.

---

## What It Does

| Manual In-Basket Workflow | This Agent |
|---|---|
| MA reads message and mentally assigns acuity | Acuity classification node: EMERGENT / URGENT / SEMI-URGENT / NON-URGENT / ADMINISTRATIVE |
| Staff checks 5-field documentation checklist manually | Documentation gap detection node — flags `requires_human_review` if gaps > 2 |
| Routing decision made by individual judgment | Pathway assignment node with acuity-to-SLA mapping |
| Escalation depends on who's paying attention | `requires_human_review = True` is a hard flag — never silent |
| Zero audit trail on routing decisions | Append-only `triage_audit_log` on every node transition, HIPAA-compliant |
| Response drafted from memory | Structured response draft generated at `response_drafted` node |

---

## System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    Patient Message Input                         │
│         (Epic In-Basket / FHIR Communication resource)           │
└────────────────────────────────┬─────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                LangGraph Triage State Machine                    │
│                                                                  │
│  [parse_intake] ──► [classify_acuity] ──► [route_to_pathway]    │
│       │                   │                      │             │
│  validation          acuity level            pathway +            │
│  check               assigned               role assigned         │
│       │                   │                      │             │
│       ▼                   ▼                      ▼             │
│  [human_review] ◄── (>2 gaps) ◄── [detect_documentation_gaps]  │
│  (if flagged)                                     │             │
│                                                   ▼             │
│                                         [finalize_audit]         │
│                                                   │             │
│                                                   ▼             │
│                                     Routing Decision +            │
│                                     Audit Event Written           │
└─────────────────────────────────────────────────────────────────┘
          │ Append-only HIPAA audit log on every node transition
          ▼
┌─────────────────────────────────────────────────────────────────┐
│  PostgreSQL: triage_audit_log (append-only)                      │
└─────────────────────────────────────────────────────────────────┘
```

### Core Design Principles

- **Every triage decision is audited** — 10 distinct event types capture the full lifecycle from message receipt to routing completion.
- **Human review flags are non-negotiable** — >2 documentation gaps or validation failures set `requires_human_review = True`, matching the MA escalation threshold in Epic workflow governance.
- **Pydantic validation at every node** — typed schemas prevent silent data corruption across the state machine.
- **HIPAA posture** — `patient_id` fields are designed for de-identified tokens. Connect live PHI only through Epic SMART-on-FHIR with a BAA in place.

---

## Epic In-Basket Workflow Context

This agent replicates the real governance logic behind Epic In-Basket triage — not a simplified approximation, but the actual decision tree that governs message routing in production ambulatory environments.

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
**App Registration:** Non-Patient-Facing Application via Epic’s vendor portal

> ⚠️ **Before connecting to a production Epic environment:** IS governance review, CMIO sign-off, and CAB approval required for any workflow that touches In-Basket routing.

---

## Audit Event Lifecycle

Every node transition writes an immutable event. No silent routing.

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

## Technology Stack

| Layer | Technology | Rationale |
|---|---|---|
| **Agent Orchestration** | LangGraph | Stateful graph — each node maps to a discrete triage decision point |
| **Pattern** | State Machine + Conditional Edges | Routing logic is branching, not sequential — LangGraph conditional edges handle escalation cleanly |
| **Data Validation** | Pydantic AI | Typed schemas enforce completeness at every node transition |
| **LLM** | OpenAI GPT-4o | Acuity classification + response drafting with structured output |
| **Audit Store** | PostgreSQL + asyncpg | Append-only HIPAA audit log — no ORM overhead on write path |
| **Language** | Python 3.11+ | Type hints throughout; async-native |

---

## Repository Structure

```
clinical-triage-agent/
├── app.py                          # Streamlit / FastAPI interface layer
├── main.py                         # LangGraph graph definition and entry point
├── requirements.txt
├── .env.example
│
├── audit/
│   ├── models.py                   # TriageAuditEvent Pydantic model (10 event types)
│   ├── logger.py                   # Append-only asyncpg writer — never raises
│   ├── queries.py                  # Acuity distribution, documentation gap summary
│   └── migrations/
│       └── 001_create_triage_audit_log.sql
│
└── tests/
    └── test_audit.py
```

---

## Compliance Posture

- **HIPAA:** `triage_audit_log` is append-only — satisfies audit log requirements for covered entities. `patient_id` stored as de-identified token by default.
- **Escalation Safety Net:** `requires_human_review = True` is a hard flag. The agent never silently routes high-acuity or documentation-incomplete messages.
- **Change Management:** In-Basket routing is a governed workflow in every Epic health system. Production deployment requires IS governance review, CMIO sign-off, and CAB approval.

---

## Known Failure Modes

Production healthcare AI needs an honest failure mode table. Here’s mine.

| Failure Mode | Impact | Mitigation |
|---|---|---|
| LLM mis-classifies EMERGENT as URGENT | Delayed escalation — patient safety risk | Confidence threshold + mandatory human review below 0.90 for EMERGENT acuity |
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

# Initialize audit log
psql $DATABASE_URL -f audit/migrations/001_create_triage_audit_log.sql

# Start agent
python main.py

# Run tests
pytest tests/ -v
```

### Environment Variables

```env
OPENAI_API_KEY=your_key_here
DATABASE_URL=postgresql://user:pass@localhost:5432/triage_db
AUDIT_LOG_ENABLED=true
HIPAA_MODE=true
HUMAN_REVIEW_GAP_THRESHOLD=2
```

---

## Roadmap

- [ ] Epic MyChart message ingestion via FHIR `Communication` resource
- [ ] Escalation agent for EMERGENT and URGENT acuity paths
- [ ] Clinician feedback loop for response draft quality scoring
- [ ] HIPAA guardrail integration via [`healthcare-compliance-guardrail`](https://github.com/jsfaulkner86/healthcare-compliance-guardrail)
- [ ] Live EHR context via [`ehr-mcp`](https://github.com/jsfaulkner86/ehr-mcp)

---

## If You're Building Healthcare AI

If this pattern is useful to you, a ⭐ helps others find it.

If you're a health system or ambulatory care group trying to reduce In-Basket burden without breaking Epic governance — this is the kind of system I architect at [The Faulkner Group](https://thefaulknergroupadvisors.com).

---

<div align="center">

*Part of The Faulkner Group’s healthcare agentic AI portfolio → [github.com/jsfaulkner86](https://github.com/jsfaulkner86)*

*Built from 14 years and 12 Epic enterprise health system deployments.*

</div>
