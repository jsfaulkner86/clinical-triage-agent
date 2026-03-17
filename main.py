from typing import TypedDict, Literal, Optional
from langgraph.graph import StateGraph, END
from pydantic import BaseModel, Field
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate

llm = ChatOpenAI(model="gpt-4", temperature=0.1)

# ── DATA MODELS ────────────────────────────────────────

class PatientIntake(BaseModel):
    patient_id: str
    chief_complaint: str
    vital_signs: Optional[str] = None
    insurance_verified: bool = False
    allergies_documented: bool = False
    medication_list: Optional[str] = None
    referring_provider: Optional[str] = None
    reason_for_visit: Optional[str] = None

class AgentState(TypedDict):
    intake: dict
    acuity_level: str
    care_pathway: str
    documentation_gaps: list
    routing_decision: str
    audit_log: list
    requires_human_review: bool

# ── ACUITY LEVELS & PATHWAYS ───────────────────────────

ACUITY_PATHWAYS = {
    "EMERGENT": "Emergency Department — immediate physician notification",
    "URGENT": "Acute Care — nurse assessment within 30 minutes",
    "SEMI-URGENT": "Scheduled Same-Day — provider queue",
    "NON-URGENT": "Scheduled Routine — next available appointment",
    "ADMINISTRATIVE": "Front Desk — non-clinical resolution"
}

REQUIRED_FIELDS = [
    "vital_signs",
    "allergies_documented",
    "medication_list",
    "reason_for_visit",
    "insurance_verified"
]

# ── NODE 1: PARSE & VALIDATE INTAKE ───────────────────

def parse_intake(state: AgentState) -> AgentState:
    log = state.get("audit_log", [])
    intake = state["intake"]

    try:
        PatientIntake(**intake)
        log.append(f"STEP 1: Intake validated for patient {intake['patient_id']}")
    except Exception as e:
        log.append(f"STEP 1: Validation error — {str(e)}")
        state["requires_human_review"] = True

    state["audit_log"] = log
    return state

# ── NODE 2: CLASSIFY ACUITY ────────────────────────────

def classify_acuity(state: AgentState) -> AgentState:
    intake = state["intake"]

    prompt = ChatPromptTemplate.from_messages([
        ("system", """You are a clinical triage specialist. Based on the 
        patient's chief complaint and available data, classify the acuity 
        level as one of: EMERGENT, URGENT, SEMI-URGENT, NON-URGENT, ADMINISTRATIVE.
        Respond with only the acuity level word."""),
        ("human", "Chief complaint: {complaint}\nReason for visit: {reason}")
    ])

    response = llm.invoke(prompt.format_messages(
        complaint=intake.get("chief_complaint", "Not provided"),
        reason=intake.get("reason_for_visit", "Not provided")
    ))

    acuity = response.content.strip().upper()
    if acuity not in ACUITY_PATHWAYS:
        acuity = "NON-URGENT"

    state["acuity_level"] = acuity
    state["audit_log"].append(f"STEP 2: Acuity classified as {acuity}")
    return state

# ── NODE 3: ROUTE TO CARE PATHWAY ─────────────────────

def route_to_pathway(state: AgentState) -> AgentState:
    acuity = state["acuity_level"]
    pathway = ACUITY_PATHWAYS.get(acuity, ACUITY_PATHWAYS["NON-URGENT"])

    state["care_pathway"] = pathway
    state["routing_decision"] = f"Patient routed to: {pathway}"
    state["audit_log"].append(f"STEP 3: Routed to {pathway}")
    return state

# ── NODE 4: FLAG DOCUMENTATION GAPS ───────────────────

def detect_documentation_gaps(state: AgentState) -> AgentState:
    intake = state["intake"]
    gaps = []

    if not intake.get("vital_signs"):
        gaps.append("Vital signs not documented")
    if not intake.get("allergies_documented"):
        gaps.append("Allergy status not confirmed")
    if not intake.get("medication_list"):
        gaps.append("Medication reconciliation incomplete")
    if not intake.get("reason_for_visit"):
        gaps.append("Reason for visit not documented")
    if not intake.get("insurance_verified"):
        gaps.append("Insurance verification pending")

    state["documentation_gaps"] = gaps
    state["requires_human_review"] = len(gaps) > 2

    if gaps:
        state["audit_log"].append(f"STEP 4: {len(gaps)} documentation gap(s) flagged")
    else:
        state["audit_log"].append("STEP 4: Documentation complete — no gaps detected")

    return state

# ── NODE 5: AUDIT LOG FINALIZATION ─────────────────────

def finalize_audit(state: AgentState) -> AgentState:
    state["audit_log"].append(
        f"STEP 5: Routing complete — Acuity: {state['acuity_level']} | "
        f"Pathway: {state['care_pathway']} | "
        f"Gaps: {len(state['documentation_gaps'])} | "
        f"Human Review Required: {state['requires_human_review']}"
    )
    return state

# ── BUILD GRAPH ────────────────────────────────────────

def build_triage_agent():
    graph = StateGraph(AgentState)

    graph.add_node("parse", parse_intake)
    graph.add_node("classify", classify_acuity)
    graph.add_node("route", route_to_pathway)
    graph.add_node("gaps", detect_documentation_gaps)
    graph.add_node("audit", finalize_audit)

    graph.set_entry_point("parse")
    graph.add_edge("parse", "classify")
    graph.add_edge("classify", "route")
    graph.add_edge("route", "gaps")
    graph.add_edge("gaps", "audit")
    graph.add_edge("audit", END)

    return graph.compile()

# ── MAIN ──────────────────────────────────────────────

if __name__ == "__main__":
    patient = {
        "patient_id": "PT-00892",
        "chief_complaint": "Severe chest pain radiating to left arm, onset 20 minutes ago",
        "vital_signs": None,
        "insurance_verified": False,
        "allergies_documented": True,
        "medication_list": "Metoprolol 25mg, Aspirin 81mg",
        "referring_provider": "Dr. Sarah Chen",
        "reason_for_visit": "Acute chest pain evaluation"
    }

    agent = build_triage_agent()
    result = agent.invoke({
        "intake": patient,
        "audit_log": [],
        "requires_human_review": False
    })

    print("\n── TRIAGE DECISION ──")
    print(f"Acuity Level: {result['acuity_level']}")
    print(f"Care Pathway: {result['care_pathway']}")
    print(f"Documentation Gaps: {result['documentation_gaps']}")
    print(f"Human Review Required: {result['requires_human_review']}")
    print("\n── AUDIT TRAIL ──")
    for entry in result["audit_log"]:
        print(f"  {entry}")
