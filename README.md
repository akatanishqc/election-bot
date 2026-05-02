# ECI Election Information Bot

A RAG-based web app that answers Indian voter queries using official ECI documents.
Built at ₹0 using HuggingFace (DeepSeek-V3 + MiniLM), Pinecone, Supabase, Next.js 14, and FastAPI.

---

## Architecture

```
election-bot/
├── frontend/   → Next.js 14 (deploy to Firebase Hosting)
└── backend/    → Python FastAPI (deploy to Render)
```

**Flow:** User sends a question → FastAPI embeds it locally (MiniLM) → queries Pinecone for relevant ECI document chunks → DeepSeek-V3 generates a grounded answer → response returned to the chat UI.

---

## Tech Stack

| Layer      | Technology                                     | Cost                |
| ---------- | ---------------------------------------------- | ------------------- |
| Frontend   | Next.js 14, TypeScript, Tailwind CSS           | ₹0 (Firebase free)  |
| Backend    | Python FastAPI                                 | ₹0 (Render free)    |
| LLM        | DeepSeek-V3 via HuggingFace Inference API      | ₹0 (free tier)      |
| Embeddings | sentence-transformers/all-MiniLM-L6-v2 (local) | ₹0                  |
| Vector DB  | Pinecone Serverless (384 dimensions, cosine)   | ₹0 (1 index free)   |
| Database   | Supabase                                       | ₹0 (500MB free)     |
| Hosting    | Firebase Hosting + Render                      | ₹0 (both free tier) |

---

## Prerequisites

- Python 3.11+
- Node.js 18+
- A HuggingFace account → [huggingface.co](https://huggingface.co)
- A Pinecone account → [pinecone.io](https://pinecone.io)
- A Supabase account → [supabase.com](https://supabase.com)
- Firebase CLI → `npm install -g firebase-tools`

---

## Local Setup

### 1. Clone the repo

```bash
git clone https://github.com/akatanishqc/election-bot.git
cd election-bot
```

### 2. Backend setup

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate      # Windows
source .venv/bin/activate   # macOS / Linux
pip install -r requirements.txt
cp .env.example .env
# Fill in your keys in .env
```

### 3. Frontend setup

```bash
cd frontend
npm install
# Create .env.local — set NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
```

### 4. Supabase table setup

Run this in Supabase → SQL Editor:

```sql
CREATE TABLE IF NOT EXISTS interaction_logs (
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

CREATE TABLE IF NOT EXISTS mode_change_log (
    id         UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    mode       TEXT NOT NULL,
    changed_at TIMESTAMPTZ NOT NULL
);
```

### 5. Pinecone index setup

Create an index with:

- **Name:** `election-bot`
- **Dimensions:** `384`
- **Metric:** `cosine`
- **Type:** Serverless (AWS, us-east-1)

### 6. Ingest ECI documents

> **Windows users:** Run ingestion on Google Colab due to a numpy/torch incompatibility.
> See the Ingestion section below.

```bash
cd backend
python ingestion/ingest.py --docs ./ingestion/eci_docs/
```

### 7. Start both servers

**Terminal 1 — Backend:**

```bash
cd backend
.venv\Scripts\activate
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
PINECONE_API_KEY=
PINECONE_INDEX_NAME=election-bot
SUPABASE_URL=               # Supabase Project Settings → General
SUPABASE_ANON_KEY=          # Supabase Project Settings → API → Legacy anon key
HUGGINGFACE_API_KEY=        # HuggingFace → Settings → Access Tokens (Inference permission)
ADMIN_SECRET_TOKEN=         # Any random string, min 32 characters
BOT_MODE=ACTIVE
ALLOWED_ORIGINS_RAW=http://localhost:3000,https://your-firebase-app.web.app
```

### frontend/.env.local

```env
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
```

---

## Ingestion (PDF → Pinecone)

The embedding model requires PyTorch which conflicts with numpy on Windows.
Run ingestion on **Google Colab**:

1. Go to [colab.research.google.com](https://colab.research.google.com)
2. Install:

```python
!pip uninstall pinecone-client -y
!pip install sentence-transformers pinecone pypdf langdetect langchain-text-splitters python-dotenv
```

3. Upload `ingest.py`, `chunker.py`, and your PDFs
4. Run:

```python
import subprocess, os
env = os.environ.copy()
env["PINECONE_API_KEY"] = "your_pinecone_key"
env["PINECONE_INDEX_NAME"] = "election-bot"
result = subprocess.run(
    ["python3", "ingest.py", "--docs", "./"],
    capture_output=True, text=True, env=env
)
print(result.stdout)
print(result.stderr)
```

For adding new documents later, use `--incremental` to skip already-ingested vectors.

---

## Deployment

### Backend → Render

1. Push repo to GitHub
2. Render → New Web Service → Root Directory: `backend`
3. Build: `pip install -r requirements.txt`
4. Start: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
5. Add all env vars from `backend/.env`
6. `backend/runtime.txt` must contain `3.11.9` (forces Python 3.11)

### Frontend → Firebase Hosting

```bash
cd frontend
npm run build
firebase deploy
```

Update `ALLOWED_ORIGINS_RAW` on Render to include your Firebase URL after deploying.

### Keep Render awake (free tier)

Set up [UptimeRobot](https://uptimerobot.com) to ping every 10 minutes:

- URL: `https://your-render-url.onrender.com/api/status`

---

## Bot Modes

| Mode         | Behaviour                                                                   |
| ------------ | --------------------------------------------------------------------------- |
| `ACTIVE`     | Fully operational. Answers all ECI-document-grounded queries.               |
| `RESTRICTED` | 48-hour silence period. Only polling station queries allowed (Section 126). |
| `PAUSED`     | Emergency shutdown. All users receive a maintenance message.                |

### ECI 3-Hour Kill Switch

1. **T+0** — `/admin` → change mode to `PAUSED`
2. **T+30** — Logs → filter Flagged=ON → identify bad chunk
3. **T+90** — Re-ingest corrected document on Colab with `--incremental`
4. **T+180** — Test → change mode back to `ACTIVE`

---

## Compliance

- **ECI March 2026 Advisory** — 3-hour takedown rule, AI-generated label on all responses
- **Section 126, RPA** — 48-hour silence period enforced via RESTRICTED mode
- **90-day interaction log** — Stored in Supabase, auto-deleted after 90 days
- **No PII stored** — Session IDs are client-generated UUIDs only

---

## Project Structure

```
election-bot/
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
│   │   │   └── LanguagePicker.tsx
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
    ├── requirements.txt
    └── runtime.txt
```

---

## Supported Languages

English · हिन्दी · বাংলা · தமிழ் · తెలుగు · മലയാളം · অসমীয়া

---

## License

MIT
