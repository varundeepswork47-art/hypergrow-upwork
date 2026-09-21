import streamlit as st
from openai import OpenAI
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

# --- Schema for Structured Output ---
class UpworkFitResult(BaseModel):
    fit_score: int = Field(description="Score between 1 and 100 for HyperGrow agency fit.")
    verdict: str = Field(description="APPLY, CAUTION, or SKIP.")
    summary: str = Field(description="One-sentence executive summary.")
    pros: list[str] = Field(description="2-3 bullet reasons why this matches HyperGrow.")
    red_flags: list[str] = Field(description="Risks, warnings, or constraints. Empty if none.")
    relevant_case_study: str = Field(description="Closest HyperGrow case study name.")
    proposal: str = Field(description="Tailored Upwork proposal ready to submit.")

# --- Page Setup ---
st.set_page_config(page_title="HyperGrow Upwork Fit Scorer", page_icon="⚡", layout="wide")
st.title("⚡ Upwork Job Scorer & Proposal Generator")
st.caption("Score job fit and generate proposals tailored to HyperGrow's portfolio.")

# Sidebar Configuration
with st.sidebar:
    st.header("Setup")
    st.text("AI Provider: OpenAI (ChatGPT)")
    
    # Read from Streamlit secrets or let user paste key
    default_key = st.secrets.get("OPENAI_API_KEY", "")
    api_key = st.text_input("OpenAI API Key", value=default_key, type="password", placeholder="sk-...")
    
    st.divider()
    st.subheader("Score Thresholds")
    apply_threshold = st.slider("Apply above", min_value=50, max_value=90, value=70)

# Single Main Input Area
job_text = st.text_area(
    "Paste Upwork Job Post",
    height=280,
    placeholder="Paste the full job post here (title, description, skills, budget, client info, or unformatted text)..."
)

if st.button("Analyze fit", type="primary"):
    if not api_key.strip():
        st.error("Please provide an OpenAI API Key in the sidebar or via Streamlit Secrets (`OPENAI_API_KEY`).")
    elif not job_text.strip():
        st.warning("Please paste a job description first.")
    else:
        with st.spinner("Evaluating job with OpenAI..."):
            try:
                client = OpenAI(api_key=api_key.strip())

                prompt = f"""
You are the business development director for HyperGrow.
Evaluate this Upwork job posting against HyperGrow's portfolio, capabilities, and target clients.

Agency Profile:
{HYPERGROW_PROFILE}

Job Posting:
{job_text}

Instructions:
1. Evaluate if this matches our capabilities: AI voice agents (Vapi, Twilio), WhatsApp/chat assistants, n8n automations, and AI SaaS applications.
2. If budget, client history, or payment verification are missing from the post, do NOT penalize the score—evaluate purely on technical and operational fit.
3. Check for specific red flags or constraints (e.g. client says "no agencies", unrealistic scope, or missing screening questions).
4. Recommendation rules:
   - Score >= {apply_threshold} -> 'APPLY'
   - Score between {apply_threshold - 15} and {apply_threshold - 1} -> 'CAUTION'
   - Score < {apply_threshold - 15} -> 'SKIP'
5. Write a punchy, tailored Upwork proposal citing the best matching HyperGrow project (e.g., RecruitKar, Vzoq, Rezume, Retail AI Kiosk, Courtyardly). If the post requires a specific keyword or phrase at the top, make sure it is included.
"""

                # Call OpenAI with native Pydantic structured output
                completion = client.beta.chat.completions.parse(
                    model="gpt-4o-mini",
                    messages=[
                        {"role": "system", "content": "You are a professional B2B agency evaluation expert."},
                        {"role": "user", "content": prompt}
                    ],
                    response_format=UpworkFitResult
                )

                result: UpworkFitResult = completion.choices[0].message.parsed

                # Top Metrics
                st.divider()
                col1, col2, col3 = st.columns(3)
                col1.metric("Fit Score", f"{result.fit_score}/100")
                col2.metric("Recommendation", result.verdict)
                col3.metric("Best Case Study", result.relevant_case_study)

                st.info(f"**Summary:** {result.summary}")

                # Two-Column Results
                col_left, col_right = st.columns(2)
                with col_left:
                    st.subheader("Why this is a fit")
                    for pro in result.pros:
                        st.markdown(f"- {pro}")

                    if result.red_flags:
                        st.subheader("Watch out for")
                        for flag in result.red_flags:
                            st.markdown(f"- ⚠️ {flag}")

                with col_right:
                    st.subheader("Tailored Proposal")
                    st.text_area("Copy Proposal", value=result.proposal, height=320)

            except Exception as e:
                st.error(f"Couldn't score this job: {e}")
