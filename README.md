# ECI Election Information Bot

A RAG-based web app that answers Indian voter queries using official ECI documents.
Built at ₹0 using Gemini 2.5 Flash-Lite, Pinecone, Supabase, Next.js 14, and FastAPI.

---

## Architecture

```
election-bot/
├── frontend/   → Next.js 14 (deploy to Vercel)
└── backend/    → Python FastAPI (deploy to Render)
```

**Flow:** User sends a question → FastAPI embeds it → queries Pinecone for relevant ECI document chunks → Gemini generates a grounded answer → response returned to the chat UI.

---

## Tech Stack

| Layer      | Technology                           | Cost                            |
| ---------- | ------------------------------------ | ------------------------------- |
| Frontend   | Next.js 14, TypeScript, Tailwind CSS | ₹0 (Vercel free)                |
| Backend    | Python FastAPI, LangChain            | ₹0 (Render free)                |
| LLM        | Gemini 2.5 Flash-Lite                | ₹0 (Google AI Studio free tier) |
| Embeddings | Google text-embedding-004            | ₹0 (free tier)                  |
| Vector DB  | Pinecone Serverless                  | ₹0 (1 index free)               |
| Database   | Supabase                             | ₹0 (500MB free)                 |
| Hosting    | Vercel + Render                      | ₹0 (both free tier)             |

---

## Prerequisites

- Python 3.11+
- Node.js 18+
- A Google AI Studio account → [aistudio.google.com](https://aistudio.google.com)
- A Pinecone account → [pinecone.io](https://pinecone.io)
- A Supabase account → [supabase.com](https://supabase.com)

---

## Local Setup

### 1. Clone the repo

```bash
git clone https://github.com/your-username/election-bot.git
cd election-bot
```

### 2. Backend setup

```bash
cd backend

# Create and activate virtual environment
python -m venv .venv

# Windows
.venv\Scripts\activate

# macOS / Linux
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create environment file
cp .env.example .env
# Fill in your keys in .env (see Environment Variables section below)
```

### 3. Frontend setup

```bash
cd frontend
npm install
cp .env.local.example .env.local
# Set NEXT_PUBLIC_API_BASE_URL=http://localhost:8000 in .env.local
```

### 4. Supabase table setup

Run this SQL once in your Supabase SQL editor:

```sql
CREATE TABLE interaction_logs (
    id            UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    created_at    TIMESTAMPTZ DEFAULT NOW(),
    session_id    TEXT NOT NULL,
    query_text    TEXT NOT NULL,
    response_text TEXT NOT NULL,
    query_language TEXT,
    sources       JSONB,
    was_refused   BOOLEAN DEFAULT FALSE,
    was_flagged   BOOLEAN DEFAULT FALSE,
    bot_mode      TEXT,
    response_ms   INTEGER,
    user_agent    TEXT
);

CREATE TABLE mode_change_log (
    id         UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    mode       TEXT NOT NULL,
    changed_at TIMESTAMPTZ NOT NULL
);
```

### 5. Ingest ECI documents

Place your ECI PDF files in `backend/eci_docs/`, then run:

```bash
cd backend
python ingestion/ingest.py --docs ./eci_docs/
```

This embeds all PDFs and uploads them to Pinecone. Run once before starting the server.

### 6. Start both servers

**Terminal 1 — Backend:**

```bash
cd backend
.venv\Scripts\activate   # Windows
uvicorn app.main:app --reload --port 8000
```

**Terminal 2 — Frontend:**

```bash
cd frontend
npm run dev
```

Open [http://localhost:3000/chat](http://localhost:3000/chat)

---

## Environment Variables

### backend/.env

```env
GEMINI_API_KEY=           # From Google AI Studio
PINECONE_API_KEY=         # From Pinecone console
PINECONE_INDEX_NAME=election-bot
SUPABASE_URL=             # From Supabase project settings
SUPABASE_ANON_KEY=        # From Supabase project settings
ADMIN_SECRET_TOKEN=       # Any random string, min 32 characters
BOT_MODE=ACTIVE           # ACTIVE | RESTRICTED | PAUSED
ALLOWED_ORIGINS=http://localhost:3000
```

### frontend/.env.local

```env
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
```

---

## Deployment

### Backend → Render

1. Push repo to GitHub
2. Go to [render.com](https://render.com) → New → Web Service
3. Connect your GitHub repo, set **Root Directory** to `backend`
4. Build command: `pip install -r requirements.txt`
5. Start command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
6. Add all env vars from `backend/.env` in the Render dashboard
7. Update `ALLOWED_ORIGINS` to include your Vercel URL once deployed

### Frontend → Vercel

1. Go to [vercel.com](https://vercel.com) → New Project
2. Import your GitHub repo, set **Root Directory** to `frontend`
3. Add env var: `NEXT_PUBLIC_API_BASE_URL` = your Render backend URL
4. Deploy

### Keep Render awake (free tier)

Set up [UptimeRobot](https://uptimerobot.com) (free) to ping your Render URL every 10 minutes:

- Monitor type: HTTP(S)
- URL: `https://your-render-url.onrender.com/api/status`
- Interval: 10 minutes

---

## Bot Modes

The bot has three operating modes, controllable from the admin dashboard at `/admin`:

| Mode         | Behaviour                                                                                       |
| ------------ | ----------------------------------------------------------------------------------------------- |
| `ACTIVE`     | Fully operational. Answers all ECI-document-grounded queries.                                   |
| `RESTRICTED` | 48-hour pre-poll silence period. Only polling station queries allowed (Section 126 compliance). |
| `PAUSED`     | Emergency shutdown. All users receive a maintenance message.                                    |

### ECI 3-Hour Kill Switch Procedure

If a misinformation report is received, you have 3 hours to act:

1. **T+0 min** — Go to `/admin` → change mode to `PAUSED`
2. **T+30 min** — Check Admin → Logs → filter Flagged=ON → identify the bad chunk
3. **T+90 min** — Delete or re-ingest the problematic document:
   ```bash
   python ingestion/ingest.py --docs ./eci_docs/corrected_file.pdf --incremental
   ```
4. **T+180 min** — Test with 3 queries → change mode back to `ACTIVE`

---

## Compliance

- **ECI March 2026 Advisory** — 3-hour takedown rule, AI-generated label on all responses
- **Section 126, Representation of the People Act** — 48-hour silence period enforced via RESTRICTED mode
- **Meta January 2026 Policy** — Domain-specific civic tool (not a general-purpose AI chatbot)
- **90-day interaction log** — Stored in Supabase, auto-deleted after 90 days
- **No PII stored** — Session IDs are client-generated UUIDs, no phone numbers or personal data

---

## Project Structure

```
election-bot/
│
├── frontend/
│   ├── app/
│   │   ├── globals.css
│   │   ├── layout.tsx
│   │   ├── providers.tsx
│   │   └── chat/page.tsx
│   ├── components/
│   │   ├── chat/
│   │   │   ├── ChatWindow.tsx
│   │   │   ├── MessageBubble.tsx
│   │   │   ├── InputBar.tsx
│   │   │   ├── SourceCitation.tsx
│   │   │   ├── SuggestedQueries.tsx
│   │   │   ├── LanguagePicker.tsx
│   │   │   └── LoadingDots.tsx (in shared/)
│   │   └── shared/
│   │       ├── Header.tsx
│   │       ├── Footer.tsx
│   │       ├── StatusBanner.tsx
│   │       └── LoadingDots.tsx
│   ├── hooks/
│   │   ├── useChat.ts
│   │   └── useBotStatus.ts
│   ├── lib/
│   │   ├── api.ts
│   │   └── constants.ts
│   ├── store/chatStore.ts
│   └── types/index.ts
│
└── backend/
    ├── app/
    │   ├── main.py
    │   ├── config.py
    │   ├── dependencies.py
    │   ├── models/schemas.py
    │   ├── routes/
    │   │   ├── chat.py
    │   │   ├── status.py
    │   │   ├── report.py
    │   │   └── admin.py
    │   ├── services/
    │   │   ├── rag_service.py
    │   │   ├── language_service.py
    │   │   └── logging_service.py
    │   └── prompts/system_prompt.py
    ├── ingestion/
    │   ├── ingest.py
    │   └── chunker.py
    └── requirements.txt
```

---

## Supported Languages

English · हिन्दी · বাংলা · தமிழ் · తెలుగు · മലയാളം · অসমীয়া

Language is auto-detected from the user's query. Responses are returned in the same language.

---

## License

MIT
