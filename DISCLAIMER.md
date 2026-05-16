# Disclaimer

**Clinical Triage Agent**
The Faulkner Group | Version 1.0.0

---

## Not a Medical Device

This software is a **reference implementation and architectural demonstration** of an AI-assisted clinical triage workflow. It is not a cleared or approved medical device under FDA 21 CFR Part 820, ISO 13485, or any other medical device regulatory framework. It has not been submitted to or reviewed by the U.S. Food and Drug Administration or any other regulatory authority.

The acuity classification, routing logic, documentation gap detection, and response drafting demonstrated in this repository are for architectural and educational purposes only. They are not intended for use in actual clinical decision-making, patient triage, or In-Basket workflow automation without independent clinical validation, regulatory review, and organizational change management approval.

---

## Not Legal or Compliance Advice

All references to HIPAA (45 CFR Part 164), Epic governance requirements, JCAHO, or other regulatory frameworks are for **architectural and informational reference only**. Consult qualified legal counsel, compliance professionals, and your organization's CMIO and IS governance team before deploying in any regulated healthcare environment.

---

## PHI and HIPAA

This codebase is designed with HIPAA-aligned patterns (`patient_id` as de-identified token, append-only audit log), but **does not by itself make any system HIPAA-compliant**. Organizations deploying systems that process Protected Health Information must:

- Conduct an independent HIPAA Security Rule risk analysis
- Execute Business Associate Agreements (BAAs) with all applicable vendors (OpenAI, database providers, cloud infrastructure)
- Validate the full Technical, Administrative, and Physical Safeguard implementation
- Confirm that `HIPAA_MODE=true` is enforced in all production deployments
- Never store raw MRN, patient name, or date of birth in the `triage_audit_log`

The Faulkner Group assumes no liability for PHI exposure, data breaches, or regulatory violations arising from the use of this codebase.

---

## Epic In-Basket Integration

All Epic FHIR R4 and In-Basket integration patterns in this codebase are reference implementations. Production Epic integration requires:

- IS governance review, CMIO sign-off, and CAB approval before any In-Basket routing automation goes live
- Completion of Epic's App Orchard registration and review process
- A signed agreement with the deploying health system
- Compliance with Epic's Non-Patient-Facing Backend Services requirements

---

## Clinical Safety

The acuity classification logic (`EMERGENT / URGENT / SEMI-URGENT / NON-URGENT / ADMINISTRATIVE`) is implemented using an LLM with a confidence threshold. LLMs can misclassify. The `requires_human_review` flag and confidence gate are not substitutes for trained clinical staff judgment. This system must operate as **decision support** — not autonomous triage — in any production clinical environment.

---

## No Warranty

This software is provided **"as is"**, without warranty of any kind. In no event shall the authors or The Faulkner Group be liable for any claim, damages, or other liability — including but not limited to patient harm, triage errors, delayed care, PHI exposure, or regulatory penalties — arising from the use of this software.

See [LICENSE](./LICENSE) for full terms.

---

*The Faulkner Group provides healthcare IT architecture advisory services. For production deployment guidance, contact [john@thefaulknergroupadvisors.com](mailto:john@thefaulknergroupadvisors.com).*
