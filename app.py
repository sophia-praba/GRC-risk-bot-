import os
import json
import streamlit as st
from datetime import datetime
from typing import Dict, List

import openai

# ---------- CONFIG ----------
st.set_page_config(
    page_title="GRC Risk Advisor Bot",
    page_icon="🛡️",
    layout="wide",
)

st.title("🛡️  GRC Risk Advisor Bot")
st.caption("Summarize compliance gaps from audit notes & map them to cyber-insurance controls.")

# ---------- OPENAI KEY ----------
openai.api_key = st.sidebar.text_input(
    "🔑  Enter your OpenAI API key", type="password"
).strip()

MODEL = st.sidebar.selectbox(
    "OpenAI model",
    options=["gpt-4o-mini", "gpt-4o", "gpt-3.5-turbo"],
    index=0,
)

# ---------- SAMPLE INPUT ----------
SAMPLE_NOTES = """
{
  "asset": "Customer database",
  "framework": "SOC 2",
  "findings": [
    {
      "control": "CC2.1",
      "status": "failed",
      "notes": "No MFA enforced for privileged users."
    },
    {
      "control": "CC6.2",
      "status": "passed",
      "notes": "Encryption at rest verified (AES-256)."
    }
  ],
  "timestamp": "2025-06-26T10:00:00Z"
}
""".strip()

with st.expander("Need a quick example? Click to autofill sample JSON."):
    if st.button("Use sample data"):
        st.session_state["audit_text"] = SAMPLE_NOTES

# ---------- USER INPUT ----------
audit_text = st.text_area(
    "📋  Paste raw audit notes / questionnaire responses (JSON or free-text)",
    key="audit_text",
    height=300,
)

run_btn = st.button("🔍  Analyze")

# ---------- OPENAI CALL ----------
def generate_summary(audit_raw: str) -> Dict:
    """Calls OpenAI Chat API and returns a structured dict."""
    sys_prompt = (
        "You are a cybersecurity GRC analyst and insurance underwriter. "
        "Input may be messy. Extract key gaps, map them to relevant controls "
        "and suggest remediation steps that would lower cyber-insurance premiums."
    )

    user_prompt = f"AUDIT_INPUT:\n{audit_raw}"

    resp = openai.ChatCompletion.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": sys_prompt},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0.2,
        max_tokens=800,
    )
    content = resp.choices[0].message.content

    # Try to coerce JSON; fallback to raw text
    try:
        return json.loads(content)
    except json.JSONDecodeError:
        return {"raw_summary": content}


# ---------- DISPLAY ----------
if run_btn:
    if not openai.api_key:
        st.error("Please enter your OpenAI key in the sidebar.")
        st.stop()

    with st.spinner("Crunching numbers…"):
        summary = generate_summary(audit_text)

    st.success("Analysis complete!")

    if "raw_summary" in summary:
        st.markdown("### 📑  Summary")
        st.markdown(summary["raw_summary"])
    else:
        st.markdown("### ⚠️  Key Gaps")
        for g in summary.get("gaps", []):
            st.write(f"- **{g['control']}**: {g['issue']}")

        st.markdown("### 🛠️  Remediation Steps")
        for r in summary.get("remediation", []):
            st.write(f"- {r}")

        st.markdown("### 💰  Insurance Impact")
        st.write(summary.get("insurance_impact", "N/A"))

    # Download button
    st.download_button(
        label="💾  Download report",
        data=json.dumps(summary, indent=2),
        file_name=f"grc_risk_report_{datetime.utcnow().date()}.json",
        mime="application/json",
    )
