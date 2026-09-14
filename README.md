# HyperGrow — Upwork Fit Scorer

Paste an Upwork job description → get a 0-100 fit score against HyperGrow's actual
services, tech stack, and past work, a verdict (Strong fit / Worth a look / Skip), and
— on demand — a personalized proposal draft. Every analysis is saved to a **History**
tab so you can revisit past jobs and drafts. Built to stop you from spending connects
on jobs that were never going to fit.

Supports **Anthropic (Claude), OpenAI, and Google (Gemini)** — pick whichever you have
an API key for in the sidebar.

## What's in here
- `app.py` — the Streamlit app
- `hypergrow_profile.py` — HyperGrow's services, stack, industries, past projects, and
  ideal-fit / red-flag signals. **Edit this file** whenever the company profile changes
  — everything else reads from it automatically.
- `requirements.txt` — dependencies
- `.streamlit/secrets.toml.example` — template for your API key(s)

## Run it locally first (optional, but worth doing once)
```bash
pip install -r requirements.txt
streamlit run app.py
```
Paste your Anthropic or OpenAI API key into the sidebar and try a real job post.

## Deploy on Streamlit Community Cloud (free)

1. **Push this folder to a GitHub repo** (can be private).
   ```bash
   cd upwork-fit-dashboard
   git init
   git add .
   git commit -m "Upwork fit scorer"
   git branch -M main
   git remote add origin https://github.com/<your-username>/<repo-name>.git
   git push -u origin main
   ```
   `.gitignore` already excludes `.streamlit/secrets.toml`, so you won't accidentally
   commit a real API key.

2. **Go to [share.streamlit.io](https://share.streamlit.io)** and sign in with GitHub.

3. **Click "New app"**, pick your repo, branch `main`, and set the main file to `app.py`.

4. **Add your API key as a secret** — in the app's dashboard, go to
   **Settings → Secrets**, and paste:
   ```toml
   ANTHROPIC_API_KEY = "sk-ant-your-real-key"
   OPENAI_API_KEY = "sk-your-real-key"
   GEMINI_API_KEY = "AIza-your-real-key"
   ```
   (You only need whichever provider you plan to use.)

5. **Deploy.** You'll get a URL like `https://your-app-name.streamlit.app` — bookmark it,
   that's your dashboard.

Once the secret is set, the sidebar API key field will auto-fill from it, so you (and
your teammates, if you share the link) don't need to paste a key every time.

## A note on history persistence
History is saved to a `history.json` file on disk next to the app, so it survives
page refreshes and between teammates using the same session. On Streamlit Community
Cloud specifically, the filesystem is **not guaranteed permanent** — it can reset when
the app redeploys, sleeps from inactivity, or you push a new commit. Use the **Export
CSV** button in the History tab periodically if you want a backup that won't disappear.
If you need guaranteed long-term history, the next step would be swapping `history.json`
for a small hosted database (e.g. a free Supabase or Google Sheet) — happy to add that
if this becomes a real need.

## Tuning it over time
- **Score feels off?** Edit the `IDEAL-FIT SIGNALS` / `RED FLAGS` sections in
  `hypergrow_profile.py` — that's the main lever.
- **New projects shipped?** Add them to `SELECTED PAST WORK` so proposals can reference
  them.
- **Thresholds** (what counts as "apply" vs "skip") are adjustable live in the sidebar
  sliders — no code change needed.
- Cost is tiny per job (one short scoring call, one short proposal call only when you
  ask for it) — a few hundred jobs a month costs a few dollars in API usage, far less
  than the connects you'll save by skipping bad-fit jobs.
