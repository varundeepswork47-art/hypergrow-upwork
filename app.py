import json
import os
import re
from datetime import datetime

import streamlit as st

from hypergrow_profile import COMPANY_NAME, COMPANY_PROFILE

st.set_page_config(page_title=f"{COMPANY_NAME} — Upwork Fit Scorer", page_icon="🎯", layout="centered")

HISTORY_PATH = os.path.join(os.path.dirname(__file__), "history.json")


def load_history() -> list:
    if not os.path.exists(HISTORY_PATH):
        return []
    try:
        with open(HISTORY_PATH, "r") as f:
            return json.load(f)
    except Exception:
        return []


def save_history_entry(entry: dict) -> None:
    history = load_history()
    history.insert(0, entry)  # newest first
    history = history[:300]  # keep it bounded
    with open(HISTORY_PATH, "w") as f:
        json.dump(history, f, indent=2)


def delete_history_entry(entry_id: str) -> None:
    history = [h for h in load_history() if h.get("id") != entry_id]
    with open(HISTORY_PATH, "w") as f:
        json.dump(history, f, indent=2)

# ----------------------------------------------------------------------------
# Sidebar: provider / API key / model / thresholds
# ----------------------------------------------------------------------------
with st.sidebar:
    st.header("Setup")

    provider = st.selectbox("AI provider", ["Anthropic (Claude)", "OpenAI", "Google (Gemini)"], index=0)

    def _get_secret(name: str) -> str:
        try:
            return st.secrets.get(name, "")
        except Exception:
            return ""

    if provider == "Anthropic (Claude)":
        default_key = _get_secret("ANTHROPIC_API_KEY")
        default_model = "claude-sonnet-5"
    elif provider == "OpenAI":
        default_key = _get_secret("OPENAI_API_KEY")
        default_model = "gpt-4o-mini"
    else:
        default_key = _get_secret("GEMINI_API_KEY")
        default_model = "gemini-2.0-flash"

    api_key = st.text_input(
        "API key",
        value=default_key,
        type="password",
        help="Leave blank if you've already set it in Streamlit secrets (recommended for a hosted app).",
    )
    model_name = st.text_input("Model name", value=default_model)

    st.divider()
    st.caption("Score thresholds")
    apply_threshold = st.slider("Apply above", 0, 100, 70)
    maybe_threshold = st.slider("Consider above", 0, apply_threshold, 40)

    st.divider()
    st.caption(
        "Your API key is only used for this session's requests and is never stored. "
        "For a hosted version, add it under the app's Streamlit Cloud → Settings → Secrets instead."
    )

# ----------------------------------------------------------------------------
# LLM calls
# ----------------------------------------------------------------------------

def _extract_json(text: str) -> dict:
    text = text.strip()
    text = re.sub(r"^```(json)?", "", text).strip()
    text = re.sub(r"```$", "", text).strip()
    match = re.search(r"\{.*\}", text, re.DOTALL)
    if match:
        text = match.group(0)
    return json.loads(text)


def call_llm(system_prompt: str, user_prompt: str, max_tokens: int = 1200) -> str:
    if provider == "Anthropic (Claude)":
        import anthropic

        client = anthropic.Anthropic(api_key=api_key)
        resp = client.messages.create(
            model=model_name,
            max_tokens=max_tokens,
            system=system_prompt,
            messages=[{"role": "user", "content": user_prompt}],
        )
        return "".join(block.text for block in resp.content if block.type == "text")
    elif provider == "OpenAI":
        from openai import OpenAI

        client = OpenAI(api_key=api_key)
        resp = client.chat.completions.create(
            model=model_name,
            max_tokens=max_tokens,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
        )
        return resp.choices[0].message.content
    else:
        from google import genai as google_genai

        client = google_genai.Client(api_key=api_key)
        resp = client.models.generate_content(
            model=model_name,
            contents=user_prompt,
            config={"system_instruction": system_prompt, "max_output_tokens": max_tokens},
        )
        return resp.text


SCORING_SYSTEM_PROMPT = f"""You are a strict, pragmatic Upwork job triager for {COMPANY_NAME}.
Score how well a pasted Upwork job description fits {COMPANY_NAME}'s services, tech stack,
and ideal-client profile, so the team doesn't waste connects on bad-fit jobs.

{COMPANY_NAME}'s profile:
{COMPANY_PROFILE}

Respond with ONLY a JSON object, no markdown fences, no preamble, in exactly this shape:
{{
  "score": <integer 0-100>,
  "verdict": "<one of: Strong fit, Worth a look, Skip>",
  "matched_services": [<0-5 short strings, services from the profile that match>],
  "matched_tech": [<0-8 short strings, tech overlaps>],
  "reasoning": [<3-6 short bullet strings explaining the score, specific to this job>],
  "red_flags": [<0-4 short bullet strings, empty list if none>],
  "suggested_connects": "<one short sentence recommending whether to spend connects, and how many if Upwork asks for a boosted bid>"
}}
Be honest and specific to the actual text of the job — don't just praise every job. A vague or
clearly bad-fit post should score low. Judge on scope match, budget realism, and red flags."""

PROPOSAL_SYSTEM_PROMPT = f"""You write short, specific Upwork proposals for {COMPANY_NAME}, an
AI product & automation studio. You are given a job description and a fit analysis.

{COMPANY_NAME}'s profile (use real project names from this if genuinely relevant — never
invent projects or numbers that aren't in this profile):
{COMPANY_PROFILE}

Write a personalized Upwork cover letter for this specific job. Rules:
- 150-250 words. No generic filler ("I am excited to apply...", "I have read your job post
  carefully..."). Open with something specific to their actual problem.
- Do NOT build the proposal around one project as a deep-dive case study. Instead, if
  relevant past work exists, mention the names of 2-3 relevant projects briefly in a single
  sentence (e.g. "we've built similar systems — X, Y, Z") to show range, not one detailed story.
  If nothing is genuinely relevant, skip past work entirely rather than forcing a weak fit.
- Reference 1-2 concrete next steps or questions that show you understood the scope, not just
  enthusiasm.
- End with a short, low-pressure call to action (e.g. offering a quick call or a short plan).
- Plain text only, no markdown headers, no bullet-point lists of your entire skill set.
- Do not use the client's name if it isn't given; don't fabricate details not in the job post."""


def score_job(job_description: str, extra_context: str) -> dict:
    user_prompt = f"JOB DESCRIPTION:\n{job_description}\n\nADDITIONAL CONTEXT:\n{extra_context or 'none'}"
    raw = call_llm(SCORING_SYSTEM_PROMPT, user_prompt, max_tokens=800)
    return _extract_json(raw)


def write_proposal(job_description: str, analysis: dict) -> str:
    user_prompt = (
        f"JOB DESCRIPTION:\n{job_description}\n\n"
        f"FIT ANALYSIS (for your context, don't repeat it verbatim):\n{json.dumps(analysis, indent=2)}"
    )
    return call_llm(PROPOSAL_SYSTEM_PROMPT, user_prompt, max_tokens=600).strip()


# ----------------------------------------------------------------------------
# Main UI
# ----------------------------------------------------------------------------
st.title(f"🎯 {COMPANY_NAME} — Upwork Fit Scorer")

tab_analyze, tab_history = st.tabs(["Analyze", "History"])

with tab_analyze:
    st.caption("Paste a job description, get a fit score, and — if it's worth it — a personalized proposal draft.")

    job_description = st.text_area("Job description", height=260, placeholder="Paste the full Upwork job post here...")
    extra_context = st.text_input(
        "Optional extra context (budget, client history, anything not in the post)",
        placeholder="e.g. Fixed price $3,000, client has 15 hires and 4.9 rating",
    )

    analyze_clicked = st.button("Analyze fit", type="primary", disabled=not job_description.strip())

    if analyze_clicked:
        if not api_key:
            st.error("Add your API key in the sidebar first.")
        else:
            with st.spinner("Scoring against HyperGrow's profile..."):
                try:
                    analysis = score_job(job_description, extra_context)
                    entry_id = datetime.now().strftime("%Y%m%d%H%M%S%f")
                    st.session_state["analysis"] = analysis
                    st.session_state["job_description"] = job_description
                    st.session_state["entry_id"] = entry_id
                    st.session_state.pop("proposal", None)
                    save_history_entry(
                        {
                            "id": entry_id,
                            "timestamp": datetime.now().isoformat(timespec="seconds"),
                            "job_snippet": job_description.strip()[:300],
                            "job_description": job_description,
                            "extra_context": extra_context,
                            "analysis": analysis,
                            "proposal": None,
                        }
                    )
                except Exception as e:
                    st.error(f"Couldn't score this job: {e}")

    if "analysis" in st.session_state:
        analysis = st.session_state["analysis"]
        score = analysis.get("score", 0)

        if score >= apply_threshold:
            badge, color = "✅ Strong fit", "green"
        elif score >= maybe_threshold:
            badge, color = "🤔 Worth a look", "orange"
        else:
            badge, color = "🚫 Skip", "red"

        col1, col2 = st.columns([1, 2])
        with col1:
            st.metric("Fit score", f"{score}/100")
        with col2:
            st.markdown(f"### :{color}[{badge}]")
            st.caption(analysis.get("suggested_connects", ""))

        st.progress(min(max(score, 0), 100) / 100)

        if analysis.get("matched_services"):
            st.markdown("**Matched services:** " + ", ".join(analysis["matched_services"]))
        if analysis.get("matched_tech"):
            st.markdown("**Matched tech:** " + ", ".join(analysis["matched_tech"]))

        st.markdown("**Why:**")
        for r in analysis.get("reasoning", []):
            st.markdown(f"- {r}")

        if analysis.get("red_flags"):
            st.markdown("**Red flags:**")
            for rf in analysis["red_flags"]:
                st.markdown(f"- ⚠️ {rf}")

        st.divider()
        generate_clicked = st.button("✍️ Generate personalized proposal")

        if generate_clicked:
            with st.spinner("Writing a personalized proposal..."):
                try:
                    proposal = write_proposal(st.session_state["job_description"], analysis)
                    st.session_state["proposal"] = proposal
                    # update the matching history entry with the generated proposal
                    history = load_history()
                    for h in history:
                        if h.get("id") == st.session_state.get("entry_id"):
                            h["proposal"] = proposal
                    with open(HISTORY_PATH, "w") as f:
                        json.dump(history, f, indent=2)
                except Exception as e:
                    st.error(f"Couldn't generate a proposal: {e}")

        if "proposal" in st.session_state:
            st.markdown("**Proposal draft** (edit before sending — always personalize further if you can):")
            st.text_area("Proposal", value=st.session_state["proposal"], height=300, label_visibility="collapsed")

with tab_history:
    st.caption("Every job you've analyzed, newest first. Saved to disk so it survives between sessions.")
    history = load_history()

    if not history:
        st.info("No history yet — analyze a job on the first tab to start building it.")
    else:
        col_a, col_b = st.columns([1, 1])
        with col_a:
            st.caption(f"{len(history)} job(s) saved")
        with col_b:
            csv_lines = ["timestamp,score,verdict,job_snippet"]
            for h in history:
                a = h.get("analysis", {})
                snippet = h.get("job_snippet", "").replace(",", ";").replace("\n", " ")
                csv_lines.append(f"{h.get('timestamp')},{a.get('score')},{a.get('verdict')},{snippet}")
            st.download_button(
                "⬇️ Export CSV",
                data="\n".join(csv_lines),
                file_name="upwork_history.csv",
                mime="text/csv",
            )

        for h in history:
            a = h.get("analysis", {})
            score = a.get("score", "?")
            verdict = a.get("verdict", "")
            with st.expander(f"[{h.get('timestamp', '')}] {score}/100 — {verdict} — {h.get('job_snippet', '')[:80]}..."):
                st.markdown("**Job description:**")
                st.text(h.get("job_description", ""))
                if h.get("extra_context"):
                    st.markdown(f"**Extra context:** {h['extra_context']}")
                st.markdown("**Why:**")
                for r in a.get("reasoning", []):
                    st.markdown(f"- {r}")
                if a.get("red_flags"):
                    st.markdown("**Red flags:**")
                    for rf in a["red_flags"]:
                        st.markdown(f"- ⚠️ {rf}")
                if h.get("proposal"):
                    st.markdown("**Saved proposal draft:**")
                    st.text_area(
                        "Saved proposal",
                        value=h["proposal"],
                        height=200,
                        label_visibility="collapsed",
                        key=f"hist_proposal_{h['id']}",
                    )
                if st.button("🗑️ Delete this entry", key=f"del_{h['id']}"):
                    delete_history_entry(h["id"])
                    st.rerun()
