# Clinical Triage Routing Agent

Multi-step LangGraph agent that classifies patient intake data, 
routes to the appropriate care pathway, and flags documentation 
gaps — modeled on real Epic In-Basket logic I architected at 
Beaumont Health System for 17,000+ annual deliveries.

## The Problem
Epic In-Basket routing is manual, inconsistent, and a leading 
cause of physician burnout. I designed the workflow logic at 
Beaumont. This is the agentic AI version of that system.

## Agent Architecture
| Step | Node | Action |
|---|---|---|
| 1 | Intake Parser | Validates and structures raw patient intake data |
| 2 | Classifier | Assigns acuity level and care pathway |
| 3 | Router | Directs to correct clinical team or queue |
| 4 | Gap Detector | Flags missing documentation before routing completes |
| 5 | Audit Logger | Records every decision with timestamp and rationale |

## Tech Stack
- LangGraph (state machine orchestration)
- PydanticAI (data validation and structured outputs)
- OpenAI GPT-4
- Python

## Why LangGraph + PydanticAI
Triage routing requires deterministic, auditable state transitions — 
not probabilistic agent chatter. LangGraph's node/edge model enforces 
the decision path. PydanticAI ensures every intake record is 
structurally valid before any routing decision fires.

## Status
🔨 In Progress — target completion April 2026
Modeled on production Epic In-Basket workflows, Beaumont Health System
