import streamlit as st
import os
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(
    page_title="Clinical Triage Agent",
    page_icon="🏥",
    layout="wide"
)

# ── STYLES ───────────────────────────────────────────────────
# Brand: Blue #6E93B0 (primary/actions), Gold #D4AE48 (interactive/checked)
st.markdown("""
<style>
/* ─ Base & Background ────────────────────────────────────── */
[data-testid="stAppViewContainer"] {
    background: #f4f3ef;
}
[data-testid="stHeader"] {
    background: transparent;
}
.block-container {
    padding-top: 2rem;
    padding-bottom: 2rem;
    max-width: 1200px;
}

/* ─ Typography ─────────────────────────────────────────── */
h1, h2, h3, .stMarkdown h1, .stMarkdown h2, .stMarkdown h3 {
    color: #1a1916 !important;
    font-weight: 700;
}
.stMarkdown p, .stMarkdown li {
    color: #2c2b28;
}

/* ─ Form container ─────────────────────────────────────── */
[data-testid="stForm"] {
    background: #ffffff;
    border: 1.5px solid #c8c5be;
    border-radius: 10px;
    padding: 1.5rem 1.75rem;
    box-shadow: 0 2px 8px rgba(0,0,0,0.06);
}

/* ─ Input labels ─────────────────────────────────────────── */
.stTextInput label,
.stTextArea label,
.stCheckbox label,
[data-baseweb="form-control-label"] {
    color: #1a1916 !important;
    font-weight: 600 !important;
    font-size: 0.875rem !important;
    letter-spacing: 0.01em;
}

/* ─ Text inputs & textareas ───────────────────────────────── */
.stTextInput input,
.stTextArea textarea {
    background: #fafaf8 !important;
    border: 1.5px solid #b0ada6 !important;
    border-radius: 6px !important;
    color: #1a1916 !important;
    font-size: 0.95rem !important;
    padding: 0.5rem 0.75rem !important;
    transition: border-color 0.15s ease, box-shadow 0.15s ease;
}
.stTextInput input:focus,
.stTextArea textarea:focus {
    border-color: #6E93B0 !important;
    box-shadow: 0 0 0 3px rgba(110,147,176,0.18) !important;
    outline: none !important;
    background: #ffffff !important;
}
.stTextInput input::placeholder,
.stTextArea textarea::placeholder {
    color: #9c9890 !important;
}

/* ─ Checkboxes ────────────────────────────────────────────── */
[data-baseweb="checkbox"] input + div {
    border: 2px solid #b0ada6 !important;
    background: #fafaf8 !important;
    border-radius: 4px !important;
}
[data-baseweb="checkbox"] input:checked + div {
    background: #D4AE48 !important;
    border-color: #D4AE48 !important;
}
.stCheckbox span {
    color: #2c2b28 !important;
    font-size: 0.9rem !important;
}

/* ─ Primary button ─────────────────────────────────────────── */
.stButton > button,
[data-testid="stFormSubmitButton"] > button {
    background: #6E93B0 !important;
    color: #ffffff !important;
    border: none !important;
    padding: 0.6rem 1.5rem !important;
    border-radius: 6px !important;
    font-weight: 700 !important;
    font-size: 0.95rem !important;
    letter-spacing: 0.02em;
    width: 100%;
    transition: background 0.15s ease, box-shadow 0.15s ease;
}
.stButton > button:hover,
[data-testid="stFormSubmitButton"] > button:hover {
    background: #4e7799 !important;
    box-shadow: 0 2px 8px rgba(110,147,176,0.30) !important;
}

/* ─ Subheaders ──────────────────────────────────────────── */
[data-testid="stHeadingWithActionElements"] h3 {
    color: #1a1916 !important;
    font-size: 1.15rem !important;
    font-weight: 700 !important;
    border-bottom: 2px solid #e0ddd8;
    padding-bottom: 0.5rem;
    margin-bottom: 1rem;
}

/* ─ Info / warning / success / error boxes ───────────────────────── */
[data-testid="stInfo"] {
    background: #eef3f7 !important;
    border-left: 4px solid #6E93B0 !important;
    color: #1a1916 !important;
    border-radius: 6px !important;
}
[data-testid="stWarning"] {
    background: #fdf3e3 !important;
    border-left: 4px solid #c87d00 !important;
    color: #1a1916 !important;
    border-radius: 6px !important;
}
[data-testid="stSuccess"] {
    background: #edf6ed !important;
    border-left: 4px solid #2e7d32 !important;
    color: #1a1916 !important;
    border-radius: 6px !important;
}
[data-testid="stError"] {
    background: #fdecea !important;
    border-left: 4px solid #c62828 !important;
    color: #1a1916 !important;
    border-radius: 6px !important;
}

/* ─ Divider ────────────────────────────────────────────────── */
[data-testid="stDivider"] hr {
    border-color: #d4d1ca !important;
}

/* ─ Acuity badge (clinical semantic — not brand colored) ────────────── */
.acuity-badge {
    display: inline-block;
    padding: 5px 16px;
    border-radius: 9999px;
    font-weight: 800;
    font-size: 1rem;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    margin-top: 4px;
}

/* ─ Audit trail ────────────────────────────────────────────── */
.audit-entry {
    font-family: 'SF Mono', 'Fira Mono', 'Consolas', monospace;
    font-size: 0.82rem;
    padding: 5px 0;
    border-bottom: 1px solid #e0ddd8;
    color: #2c2b28;
    line-height: 1.5;
}
.audit-block {
    background: #ffffff;
    border: 1.5px solid #c8c5be;
    border-radius: 8px;
    padding: 0.75rem 1rem;
}

/* ─ Results panel placeholder ──────────────────────────────── */
.empty-state {
    padding: 3rem 2rem;
    text-align: center;
    color: #7a7974;
    border: 1.5px dashed #c8c5be;
    border-radius: 10px;
    background: #ffffff;
    font-size: 0.95rem;
    line-height: 1.6;
}
</style>
""", unsafe_allow_html=True)

# ── HEADER ───────────────────────────────────────────────────
st.markdown("## 🏥 Clinical Triage Agent")
st.markdown("**LangGraph-powered patient intake, acuity classification, and care pathway routing** · The Faulkner Group")
st.divider()

# ── API KEY CHECK ────────────────────────────────────────────────
perplexity_key = os.getenv("PERPLEXITYAI_API_KEY")
if not perplexity_key:
    try:
        perplexity_key = st.secrets.get("PERPLEXITYAI_API_KEY", "")
    except Exception:
        perplexity_key = ""
if not perplexity_key:
    st.error("⚠️ PERPLEXITYAI_API_KEY not found. Add it to your Streamlit secrets or .env file.")
    st.code('[secrets]\nPERPLEXITYAI_API_KEY = "pplx-..."', language="toml")
    st.stop()

# ── IMPORT AGENT (after key check) ─────────────────────────────────
from typing import TypedDict, Optional
from langgraph.graph import StateGraph, END
from pydantic import BaseModel
from langchain_perplexity import ChatPerplexity
from langchain.prompts import ChatPromptTemplate

ACUITY_PATHWAYS = {
    "EMERGENT": "Emergency Department — immediate physician notification",
    "URGENT": "Acute Care — nurse assessment within 30 minutes",
    "SEMI-URGENT": "Scheduled Same-Day — provider queue",
    "NON-URGENT": "Scheduled Routine — next available appointment",
    "ADMINISTRATIVE": "Front Desk — non-clinical resolution"
}

# Clinical semantic colors — intentionally NOT brand colors
ACUITY_COLORS = {
    "EMERGENT": "#b91c1c",
    "URGENT": "#c2410c",
    "SEMI-URGENT": "#b45309",
    "NON-URGENT": "#15803d",
    "ADMINISTRATIVE": "#1d4ed8"
}

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

@st.cache_resource
def get_llm():
    return ChatPerplexity(
        model="sonar",
        temperature=0.1,
        pplx_api_key=os.getenv("PERPLEXITYAI_API_KEY") or perplexity_key
    )

def parse_intake(state: AgentState) -> AgentState:
    log = state.get("audit_log", [])
    intake = state["intake"]
    try:
        PatientIntake(**intake)
        log.append(f"STEP 1 ✓  Intake validated for patient {intake['patient_id']}")
    except Exception as e:
        log.append(f"STEP 1 ✗  Validation error — {str(e)}")
        state["requires_human_review"] = True
    state["audit_log"] = log
    return state

def classify_acuity(state: AgentState) -> AgentState:
    intake = state["intake"]
    llm = get_llm()
    prompt = ChatPromptTemplate.from_messages([
        ("system", """You are a clinical triage specialist. Based on the patient's chief complaint
        and available data, classify the acuity level as exactly one of:
        EMERGENT, URGENT, SEMI-URGENT, NON-URGENT, ADMINISTRATIVE.
        Respond with ONLY the acuity level word, nothing else."""),
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
    state["audit_log"].append(f"STEP 2 ✓  Acuity classified as {acuity}")
    return state

def route_to_pathway(state: AgentState) -> AgentState:
    acuity = state["acuity_level"]
    pathway = ACUITY_PATHWAYS.get(acuity, ACUITY_PATHWAYS["NON-URGENT"])
    state["care_pathway"] = pathway
    state["routing_decision"] = f"Patient routed to: {pathway}"
    state["audit_log"].append(f"STEP 3 ✓  Routed to {pathway}")
    return state

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
    msg = f"STEP 4 ✓  {len(gaps)} documentation gap(s) flagged" if gaps else "STEP 4 ✓  Documentation complete — no gaps detected"
    state["audit_log"].append(msg)
    return state

def finalize_audit(state: AgentState) -> AgentState:
    state["audit_log"].append(
        f"STEP 5 ✓  Routing complete — Acuity: {state['acuity_level']} | "
        f"Pathway: {state['care_pathway']} | "
        f"Gaps: {len(state['documentation_gaps'])} | "
        f"Human Review: {state['requires_human_review']}"
    )
    return state

@st.cache_resource
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

# ── LAYOUT ───────────────────────────────────────────────────
col_left, col_right = st.columns([1, 1], gap="large")

with col_left:
    st.subheader("Patient Intake")

    with st.form("triage_form"):
        patient_id = st.text_input("Patient ID", value="PT-00892")
        chief_complaint = st.text_area(
            "Chief Complaint *",
            value="Severe chest pain radiating to left arm, onset 20 minutes ago",
            height=80
        )
        reason_for_visit = st.text_input(
            "Reason for Visit",
            value="Acute chest pain evaluation"
        )
        vital_signs = st.text_input(
            "Vital Signs",
            placeholder="e.g. BP 142/88, HR 96, SpO2 97%, Temp 98.6°F",
            value=""
        )
        medication_list = st.text_input(
            "Medication List",
            value="Metoprolol 25mg, Aspirin 81mg"
        )
        referring_provider = st.text_input("Referring Provider", value="Dr. Sarah Chen")

        col_a, col_b = st.columns(2)
        with col_a:
            insurance_verified = st.checkbox("Insurance Verified", value=False)
        with col_b:
            allergies_documented = st.checkbox("Allergies Documented", value=True)

        submitted = st.form_submit_button("▶ Run Triage Agent", type="primary")

# ── RESULTS ───────────────────────────────────────────────────
with col_right:
    st.subheader("Triage Decision")

    if submitted:
        intake_data = {
            "patient_id": patient_id or "PT-UNKNOWN",
            "chief_complaint": chief_complaint,
            "vital_signs": vital_signs if vital_signs.strip() else None,
            "insurance_verified": insurance_verified,
            "allergies_documented": allergies_documented,
            "medication_list": medication_list if medication_list.strip() else None,
            "referring_provider": referring_provider if referring_provider.strip() else None,
            "reason_for_visit": reason_for_visit if reason_for_visit.strip() else None
        }

        with st.spinner("Running 5-node LangGraph triage workflow..."):
            try:
                agent = build_triage_agent()
                result = agent.invoke({
                    "intake": intake_data,
                    "audit_log": [],
                    "requires_human_review": False
                })

                acuity = result["acuity_level"]
                color = ACUITY_COLORS.get(acuity, "#374151")

                # Acuity badge
                st.markdown(
                    f'<div style="margin-bottom:1.25rem">'
                    f'<span style="font-size:0.72rem;color:#7a7974;text-transform:uppercase;letter-spacing:0.12em;font-weight:600">Acuity Level</span><br>'
                    f'<span class="acuity-badge" style="background:{color};color:#ffffff">{acuity}</span>'
                    f'</div>',
                    unsafe_allow_html=True
                )

                # Pathway
                st.markdown("**Care Pathway**")
                st.info(result["care_pathway"])

                # Human review flag
                if result["requires_human_review"]:
                    st.warning("⚠️ Human review required")
                else:
                    st.success("✓ No human review required")

                # Documentation gaps
                gaps = result["documentation_gaps"]
                st.markdown(f"**Documentation Gaps ({len(gaps)})**")
                if gaps:
                    for g in gaps:
                        st.markdown(
                            f'<div style="display:flex;align-items:center;gap:8px;padding:4px 0;border-bottom:1px solid #e0ddd8">'
                            f'<span style="color:#b91c1c;font-weight:700">●</span>'
                            f'<span style="color:#2c2b28;font-size:0.9rem">{g}</span>'
                            f'</div>',
                            unsafe_allow_html=True
                        )
                else:
                    st.success("✓ None — all fields complete")

                # Audit trail
                st.markdown("**Audit Trail**")
                audit_html = "".join(
                    f'<div class="audit-entry">{entry}</div>'
                    for entry in result["audit_log"]
                )
                st.markdown(f'<div class="audit-block">{audit_html}</div>', unsafe_allow_html=True)

            except Exception as e:
                st.error(f"Agent error: {str(e)}")
                st.exception(e)
    else:
        st.markdown(
            '<div class="empty-state">'
            'Fill in patient intake data and click <strong>Run Triage Agent</strong><br>'
            'to see the triage decision, care pathway, documentation gaps, and audit trail.'
            '</div>',
            unsafe_allow_html=True
        )

# ── FOOTER ───────────────────────────────────────────────────
st.divider()
st.markdown(
    '<p style="text-align:center;color:#9c9890;font-size:0.8rem">'
    'Clinical Triage Agent · Built with LangGraph + Perplexity Sonar · '
    '<a href="https://thefaulknergroupadvisors.com" style="color:#6E93B0;font-weight:600">The Faulkner Group</a>'
    '</p>',
    unsafe_allow_html=True
)
