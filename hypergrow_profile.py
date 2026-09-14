"""
Static context about HyperGrow, used to ground the LLM's scoring and
proposal-writing. Edit this file whenever the company's services, stack,
or ideal-client profile changes — everything else in the app reads from here.
"""

COMPANY_NAME = "HyperGrow"

COMPANY_PROFILE = """
HyperGrow is an AI product & automation studio based in Indore, India, founded in 2025.
We design, build, and run AI systems for businesses in North America and India.

WHAT WE STAND FOR
- Production over prototypes: if it doesn't run in the real world, it isn't done.
- Own the outcome: we stay accountable after launch, not just until handover.
- Clarity over hype: plain answers on what AI can and can't do.

SERVICES (5 practices)
1. AI voice agents — inbound support lines, qualification calls, appointment booking, AI phone interviews
2. WhatsApp & chat assistants — customer support, lead qualification, multilingual answers from a knowledge base
3. AI workflow automation — CRM & lead nurturing, event journeys, content publishing, document generation
4. AI SaaS products — multi-tenant platforms, dashboards, subscriptions & billing, white-label products
5. Applied AI & integration — knowledge bases (RAG), computer vision & OCR, LLMs inside existing systems

TECH STACK WE'RE STRONGEST IN
- LLMs: OpenAI, Claude, Gemini, Hugging Face, open-source models
- Voice: Vapi, Twilio, ElevenLabs, Deepgram, Google Speech
- Messaging: WhatsApp Business, Instagram, Telegram, Email
- Automation/agents: n8n, Zapier, Make, LangChain
- Engineering: Python, FastAPI, Node.js, TypeScript, Next.js, React
- Data/cloud: PostgreSQL, Redis, MongoDB, Docker, AWS, Vercel
- Business systems: HubSpot, Zoho, Stripe, Razorpay, Shopify

INDUSTRIES WE'VE SHIPPED IN
Recruitment & HR, B2B sales, Education & careers, Retail & grocery, Insurance,
Real estate, Food & beverage, Logistics.

SELECTED PAST WORK (use these as evidence that we've shipped in this space — when
writing a proposal, briefly mention the ones that overlap with the client's need
by name, as a short list showing range, NOT as a single deep-dive case study)
- RecruitKar (Recruitment & HR, India): AI recruiter that sources, screens, contacts,
  and interviews candidates in one platform. 7 sourcing channels, outreach by email/
  WhatsApp/AI voice, proctored AI video interviews in 10+ languages. Next.js, TypeScript,
  Node.js, PostgreSQL, Python.
- Vzoq (B2B sales, India & US): multi-tenant AI platform for lead discovery, enrichment,
  AI-personalized outbound email sequences, built-in CRM sync/portal/billing. FastAPI,
  Next.js, PostgreSQL, Redis, OpenAI, HubSpot.
- Rezume (Career tech, Canada): AI resume builder for newcomers to Canada to beat ATS
  systems — ATS scoring, job-tailored rewrites, LinkedIn import, white-labelled
  subscriptions. Next.js, TypeScript, Prisma, Claude, Stripe.
- In-store AI kiosk (Retail, Puerto Rico): shoppers ask by voice/text/photo and get the
  exact aisle, in Spanish or English. 1,480 products mapped to 45 store zones. React,
  Node.js, PostgreSQL, OpenAI, Google Cloud.
- Multilingual insurance assistant (Insurance, US): WhatsApp + phone agent answering
  policy questions only from approved company knowledge, in whatever language the
  customer uses, 24/7. WhatsApp, Twilio, OpenAI, Google Cloud, Python.
- Courtyardly (Edtech, India & US): end-to-end webinar registration journey — CRM sync,
  region-aware WhatsApp invites, reminders/follow-ups, built on n8n + HubSpot.
- Other shipped work: AI interview coach, AI career-pathway planner, voice-AI oral exams,
  Hinglish real-estate voice agent, Hindi/English food-ordering assistant, Instagram DM
  assistant, social auto-publishing, OCR-based flyer price checker.

ENGAGEMENT MODELS
- Project build: fixed scope, milestones, defined launch date — best for a specific
  AI product, agent, or automation.
- Dedicated AI team: an ongoing monthly team — best for an evolving AI roadmap.
- Care & optimisation: monitoring, fixes, improvements — best for AI systems already live.

IDEAL-FIT SIGNALS (score these UP)
- Job asks for exactly one of the 5 services above, or a close variant.
- Tech stack overlaps with our stack.
- Client wants something running in production, not just a slide deck or "advice."
- Realistic budget for scope (custom AI builds are rarely won on rock-bottom budgets).
- Client industry matches or is adjacent to our shipped industries.
- Long-term/retainer potential (dedicated team or care & optimisation fit).

RED FLAGS (score these DOWN)
- Pure no-code "just connect Zapier" busywork with near-zero budget.
- Generic web design / copywriting / SEO / data entry with no AI component.
- Budget is clearly incompatible with the stated scope (e.g. "build a full SaaS
  platform" for $50).
- Requires on-site presence outside India/North America, or a full-time employee
  role rather than a contract/project.
- Vague "looking for a rockstar AI expert" posts with no real scope — usually a sign
  of scope creep and haggling ahead.
- Asks for free trial work, unpaid samples, or working "on spec" before hire.
"""
