# Clinical Triage Agent

> **LangGraph + Pydantic AI** — Epic In-Basket logic rebuilt as an agentic triage system

[![Python](https://img.shields.io/badge/Python-3776AB?style=flat-square&logo=python&logoColor=white)]()
[![LangGraph](https://img.shields.io/badge/LangGraph-FF6B35?style=flat-square)]()
[![Pydantic](https://img.shields.io/badge/Pydantic-E92063?style=flat-square&logo=pydantic&logoColor=white)]()
[![Epic EHR](https://img.shields.io/badge/Epic-EHR-red?style=flat-square)]()

## The Problem

Epic In-Basket is one of the most overloaded workflows in healthcare. Nurses and MAs spend hours triaging messages that could be intelligently routed, prioritized, and pre-drafted by an AI system. This agent models that triage logic as a structured, stateful pipeline.

## What It Does

A stateful triage agent built with LangGraph and Pydantic AI that:
- Accepts incoming patient messages (simulating In-Basket input)
- Classifies urgency, message type, and required action
- Routes to the appropriate care team role
- Drafts a suggested response for clinician review
- Validates all outputs against a typed Pydantic schema

## Tech Stack

| Layer | Technology |
|---|---|
| Agent Framework | LangGraph |
| Data Validation | Pydantic AI |
| LLM | OpenAI GPT-4 |
| Language | Python 3.11+ |

## Getting Started

```bash
git clone https://github.com/jsfaulkner86/clinical-triage-agent
cd clinical-triage-agent
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
python main.py
```

## Environment Variables

```
OPENAI_API_KEY=your_key_here
```

## Background

Built by [John Faulkner](https://linkedin.com/in/johnathonfaulkner), Agentic AI Architect and founder of [The Faulkner Group](https://thefaulknergroupadvisors.com). Directly informed by In-Basket workflow design and clinical operations experience across 12 Epic enterprise health systems.

## What's Next
- Epic MyChart message integration via FHIR
- Escalation agent for high-urgency triage paths
- Feedback loop for clinician response training data

---
*Part of a portfolio of healthcare agentic AI systems. See all projects at [github.com/jsfaulkner86](https://github.com/jsfaulkner86)*
