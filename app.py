import json
import time
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

# --- Schema for Structured Output ---
class UpworkFitResult(BaseModel):
    fit_score: int = Field(description="Score between 1 and 100 for HyperGrow agency fit.")
    verdict: str = Field(description="APPLY, CAUTION, or SKIP.")
    summary: str = Field(description="One-sentence executive summary.")
    pros: list[str] = Field(description="2-3 bullet reasons why this matches HyperGrow.")
    red_flags: list[str] = Field(description="Risks or warnings. Empty if none.")
    relevant_case_study: str = Field(description="Closest HyperGrow case study name.")
    proposal: str = Field(description="Tailored Upwork proposal ready to submit.")

# --- Page Setup ---
st.set_page_config(page_title="HyperGrow Upwork Fit Scorer", page_icon="⚡", layout="wide")
st.title("Upwork Job Scorer & Proposal Generator")
st.caption("Score job fit and generate proposals tailored to HyperGrow's portfolio.")

# Sidebar Configuration
with st.sidebar:
    st.header("Setup")
    st.text("AI Provider: Google Gemini")
    
    default_key = st.secrets.get("GEMINI_API_KEY", "")
    api_key = st.text_input("Gemini API Key", value=default_key, type="password")
    
    st.divider()
    st.subheader("Score Thresholds")
    apply_threshold = st.slider("Apply above", min_value=50, max_value=90, value=70)

# Main Job Input Area (Single column for everything)
job_text = st.text_area(
    "Paste Upwork Job Post",
    height=280,
    placeholder="Paste the full job post here (title, description, skills, budget/client info if present)..."
)

if st.button("Analyze fit", type="primary"):
    if not api_key.strip():
        st.error("Please provide a Gemini API Key in the sidebar or via `.streamlit/secrets.toml`.")
    elif not job_text.strip():
        st.warning("Please paste a job description first.")
    else:
        client = genai.Client(api_key=api_key.strip())

        prompt = f"""
You are the business development lead for HyperGrow.
Evaluate this Upwork job posting against HyperGrow's portfolio and core capabilities.

Agency Profile:
{HYPERGROW_PROFILE}

Job Posting:
{job_text}

Evaluation Rules:
1. Score from 1-100 based on technical and operational alignment:
   - Voice agents (Vapi, Twilio, ElevenLabs)
   - WhatsApp & chat agents (RAG, multilingual)
   - Automations (n8n, Zapier, HubSpot integrations)
   - AI SaaS engineering (FastAPI, Next.js, PostgreSQL)
2. If budget, client history, or payment verification are missing, DO NOT penalize the score. Evaluate based purely on the technical requirements and project scope.
3. Recommendation rules:
   - Score >= {apply_threshold} -> 'APPLY'
   - Score between {apply_threshold - 15} and {apply_threshold - 1} -> 'CAUTION'
   - Score < {apply_threshold - 15} -> 'SKIP'
4. Provide a punchy, tailored Upwork proposal citing the best matching HyperGrow project (e.g., RecruitKar, Vzoq, Rezume, Retail AI Kiosk, or Courtyardly).
"""

        # Priority model cascade: Try primary, fallback to alternates if 503/429 occurs
        candidate_models = ["gemini-3.6-flash", "gemini-2.5-flash", "gemini-1.5-flash"]
        response = None
        used_model = None

        with st.spinner("Evaluating job with Gemini..."):
            for model_name in candidate_models:
                try:
                    response = client.models.generate_content(
                        model=model_name,
                        contents=prompt,
                        config=types.GenerateContentConfig(
                            response_mime_type="application/json",
                            response_schema=UpworkFitResult,
                        ),
                    )
                    used_model = model_name
                    break  # Request succeeded, exit cascade
                except Exception as err:
                    err_msg = str(err)
                    # If server is overloaded (503) or rate-limited (429), try next model
                    if "503" in err_msg or "UNAVAILABLE" in err_msg:
                        st.warning(f"Model `{model_name}` is experiencing high Google demand (503). Retrying with backup model...")
                        time.sleep(1.5)
                        continue
                    elif "429" in err_msg or "RESOURCE_EXHAUSTED" in err_msg:
                        st.warning(f"Model `{model_name}` reached free-tier rate limit (429). Trying fallback model...")
                        time.sleep(1.5)
                        continue
                    else:
                        st.error(f"Error on {model_name}: {err_msg}")
                        break

        if response and response.text:
            try:
                data = json.loads(response.text)

                # Render Metrics
                st.divider()
                col1, col2, col3 = st.columns(3)
                col1.metric("Fit Score", f"{data.get('fit_score', 0)}/100")
                col2.metric("Recommendation", data.get("verdict", "N/A"))
                col3.metric("Best Case Study", data.get("relevant_case_study", "N/A"))

                st.info(f"**Summary:** {data.get('summary', '')} *(Generated using {used_model})*")

                # Two-Column Results
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
                    st.text_area("Copy Proposal", value=data.get("proposal", ""), height=320)

            except Exception as parse_err:
                st.error(f"Failed to parse response: {parse_err}")
        elif not response:
            st.error("All Gemini models are temporarily at peak traffic capacity. Please wait 30 seconds and click 'Analyze fit' again.")
