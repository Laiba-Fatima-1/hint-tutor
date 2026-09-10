# Hint, Don't Solve — Web App

A deployable web version of the original `hint-tutor-agent` prototype: a
FastAPI backend wrapping the classify → pick-policy → generate pipeline, and
a React frontend with a chalkboard-themed chat UI where every tutor reply is
tagged with the teaching strategy it used (Hint, Socratic Question, Concept
Explanation, Partial-Code Feedback, or Refuse & Redirect).

```
hint-tutor-web/
├── backend/     FastAPI app — see backend/README.md to run/deploy
└── frontend/    Vite + React app — see frontend/README.md to run/deploy
```

## Fastest path to a live demo

1. **Backend → Render** (free): deploy `backend/`, add your `GEMINI_API_KEY`
   env var. You get a URL like `https://hint-tutor-api.onrender.com`.
2. **Frontend → Vercel** (free): deploy `frontend/`, set `VITE_API_URL` to
   that backend URL.
3. Open the Vercel URL — that's your live demo link.

Full details, including monorepo "Root Directory" settings, are in each
folder's README.

## Local development

Two terminals:

```bash
# terminal 1
cd backend
pip install -r requirements.txt
export GEMINI_API_KEY=your-key-here
uvicorn main:app --reload

# terminal 2
cd frontend
npm install
npm run dev
```

Frontend defaults to `http://localhost:8000` for the API — override with a
`.env` file (`VITE_API_URL=...`) if your backend runs elsewhere.

## What's different from the original prototype

The original `src/agent.py` ran as a batch script over `data/scenarios.json`
and wrote `reports/raw_results.json`. `backend/agent_core.py` is the same
classify/generate logic, refactored into functions that take one student
message at a time so the API can call it per-request. `src/evaluate.py`
(the leakage-check scorer) isn't wired into the web app — it's still useful
for offline evaluation against your own test scenarios, unchanged.
