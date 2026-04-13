# Contributing to Clinical Triage Agent

Epic In-Basket routing was designed for a different era. This agent rebuilds that logic as a modern agentic triage system — stateful, explainable, and built for the complexity of real clinical workloads.

If you've built or operated clinical triage workflows — in Epic, in an ED, in a contact center — your domain knowledge is the most valuable contribution you can make.

This project is maintained by [John Faulkner](https://linkedin.com/in/johnathonfaulkner) and [The Faulkner Group](https://thefaulknergroupadvisors.com).

---

## What We're Building

A LangGraph + PydanticAI multi-agent system that replicates and extends Epic In-Basket triage logic: classifying clinical messages, assigning priority, routing to the appropriate care team role, and generating structured handoff documentation.

---

## Ways to Contribute

- **New triage categories** — Add or refine message classification rules for specialties not yet covered
- **Routing logic improvements** — Better priority scoring, edge case handling, or specialty-specific escalation paths
- **LangGraph graph improvements** — State schema refinements, new node types, conditional edge logic
- **PydanticAI schema work** — Stronger structured output models for triage decisions and handoff docs
- **Epic parity** — Document gaps between current agent behavior and real-world Epic In-Basket routing behavior
- **Test scenarios** — Synthetic clinical messages with expected triage outcomes for regression testing
- **Documentation** — Clearer architecture explanations, clinical context, example message walkthroughs
- **Bug reports** — Open an issue with the message type and classification error

---

## Getting Started

```bash
git clone https://github.com/jsfaulkner86/clinical-triage-agent
cd clinical-triage-agent
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env  # add your LLM API key
```

To run the Streamlit UI:

```bash
streamlit run app.py
```

To run the CLI:

```bash
python main.py
```

No EHR connection required for development. All test scenarios use synthetic clinical messages.

---

## Contribution Guidelines

- **No PHI in commits** — All test messages, examples, and fixtures must be synthetic or fully de-identified. No real patient names, MRNs, DOBs, or clinical details.
- **One concern per PR** — Triage logic changes and infrastructure changes are separate PRs.
- **Document the clinical context** — If you add a new triage category or routing path, explain what real-world workflow it maps to. Epic In-Basket background is helpful but not required.
- **HIPAA awareness** — Any contribution touching message ingestion, logging, or audit trails must explicitly address PHI handling in the PR description.
- **Follow existing patterns** — LangGraph nodes and edges live in `main.py`; Pydantic models in `schemas.py` (if present); agent logic in `app.py`. Structural changes need a documented rationale.
- **Python 3.11+** — Type hints on all functions. Pydantic v2 for all structured models. Async-first where relevant.

---

## Opening an Issue

Use GitHub Issues for:
- Classification bugs (include the message type, expected routing, and actual routing)
- Feature requests (describe the clinical workflow first, then the technical ask)
- Epic In-Basket parity gaps you've identified from real-world experience

Clinical operations experience — especially Epic In-Basket, nurse triage, or care coordination — is highly relevant context. Include it.

---

## Code of Conduct

This project exists to reduce clinical administrative burden and improve care team efficiency. Contributions should reflect that mission. Be respectful, be precise, and remember that triage decisions affect real patient care.
