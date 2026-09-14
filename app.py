import json
import streamlit as st
from google import genai
from google.genai import types
from pydantic import BaseModel, Field

# Import the HyperGrow profile
try:
    from hypergrow_profile import HYPERGROW_PROFILE
except ImportError:
    HYPERGROW_PROFILE = (
        "HyperGrow is an AI product & automation studio based in Indore, India. "
        "Core capabilities: AI Voice Agents (Vapi, Twilio, ElevenLabs), "
        "WhatsApp & Chat Assistants, AI Workflow Automation (n8n, Zapier), "
        "and AI SaaS Products (FastAPI, Next.js, PostgreSQL). "
        "Key projects: RecruitKar, Vzoq, Rezume, Retail AI kiosk, Courtyardly."
    )

# --- Structured Output Schema ---
class UpworkFitResult(BaseModel):
    fit_score: int = Field(description="Score between 1 and 100 for HyperGrow fit.")
    verdict: str = Field(description="APPLY, CAUTION, or SKIP.")
    summary: str = Field(description="One-sentence executive summary.")
    pros: list[str] = Field(description="2-3 reasons why this matches HyperGrow.")
    red_flags: list[str] = Field(description="Risks or warnings. Empty if none.")
    relevant_case_study: str = Field(description="Closest HyperGrow case study.")
    proposal: str = Field(description="Tailored Upwork proposal ready to submit.")

# --- Streamlit UI Config ---
st.set_page_config(page_title="HyperGrow Upwork Fit Scorer", page_icon="⚡", layout="wide")

st.title("Upwork Job Scorer & Proposal Generator")
st.caption("Evaluate Upwork jobs against HyperGrow's core strengths without wasting connects.")

# Sidebar: Provider & Secrets setup
with st.sidebar:
    st.header("Setup")
    provider = st.selectbox("AI provider", ["Google (Gemini)"], index=0)
    
    # Check secrets or allow manual input
    default_key = st.secrets.get("GEMINI_API_KEY", "")
    api_key = st.text_input("API key", value=default_key, type="password")
    
    st.divider()
    st.subheader("Score thresholds")
    apply_threshold = st.slider("Apply above", min_value=50, max_value=90, value=70)

# Main Job Input Area
job_text = st.text_area(
    "Paste Upwork Job Post",
    height=260,
    placeholder="Paste the full job post here (including title, description, skills, and any budget/client details if available)..."
)

if st.button("Analyze fit", type="primary"):
    if not api_key.strip():
        st.error("Please enter a Gemini API Key in the sidebar or in `.streamlit/secrets.toml`.")
    elif not job_text.strip():
        st.warning("Please paste a job description first.")
    else:
        with st.spinner("Analyzing fit against HyperGrow profile..."):
            try:
                # Initialize Gemini Client
                client = genai.Client(api_key=api_key.strip())

                prompt = f"""
You are the business development director for HyperGrow.
Evaluate this Upwork job posting against HyperGrow's portfolio, capabilities, and target clients.

Agency Profile:
{HYPERGROW_PROFILE}

Upwork Job Posting:
{job_text}

Instructions:
1. Evaluate if this matches our capabilities: AI voice agents, WhatsApp/chat assistants, n8n automations, and AI SaaS applications.
2. If budget, client history, or payment status are not provided in the post, do not penalize the score—evaluate purely on technical and operational fit.
3. Recommend:
   - APPLY if score >= {apply_threshold}
   - CAUTION if score is between {apply_threshold - 15} and {apply_threshold - 1}
   - SKIP if score < {apply_threshold - 15}
4. Write a tailored proposal highlighting the most relevant case study (e.g., RecruitKar, Vzoq, Rezume, Retail AI Kiosk, Courtyardly).
"""

                # Automatically using gemini-2.5-flash with structured JSON schema
                response = client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        response_mime_type="application/json",
                        response_schema=UpworkFitResult,
                        temperature=0.2,
                    ),
                )

                data = json.loads(response.text)

                # Display Results
                st.divider()
                col1, col2, col3 = st.columns(3)
                col1.metric("Fit Score", f"{data['fit_score']}/100")
                col2.metric("Recommendation", data["verdict"])
                col3.metric("Best Case Study", data["relevant_case_study"])

                st.info(data["summary"])

                col_left, col_right = st.columns(2)
                with col_left:
                    st.subheader("Why this is a fit")
                    for pro in data.get("pros", []):
                        st.markdown(f"- {pro}")

                    if data.get("red_flags"):
                        st.subheader("Watch out for")
                        for flag in data.get("red_flags", []):
                            st.markdown(f"- ⚠️ {flag}")

                with col_right:
                    st.subheader("Tailored Proposal")
                    st.text_area("Copy Proposal", value=data.get("proposal", ""), height=300)

            except Exception as e:
                st.error(f"Couldn't score this job: {e}")
