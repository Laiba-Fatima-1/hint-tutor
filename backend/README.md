# Backend — Hint, Don't Solve API

FastAPI wrapper around the original `agent.py` classify → pick-policy →
generate pipeline. Same Gemini free-tier logic, exposed as one endpoint
instead of a batch script.

- `POST /api/tutor` — body `{"message": "...", "code": "optional"}`, returns
  `{category, policy, policy_label, policy_color, response}`
- `GET /api/health` — confirms the server is up and whether an API key is
  configured

## Run locally

```bash
pip install -r requirements.txt
cp .env.example .env      # add your GEMINI_API_KEY
export $(cat .env | xargs)
uvicorn main:app --reload
```

Server runs on `http://localhost:8000`.

## Deploy to Render (free tier)

1. Push this `backend/` folder to a GitHub repo (or the monorepo root, and
   set Root Directory to `backend` when creating the service).
2. In Render: **New** → **Web Service** → connect the repo.
3. Render should pick up `render.yaml` automatically. If configuring by
   hand instead:
   - Build command: `pip install -r requirements.txt`
   - Start command: `uvicorn main:app --host 0.0.0.0 --port $PORT`
4. Add environment variables:
   - `GEMINI_API_KEY` — get a free one at https://aistudio.google.com/apikey
   - `FRONTEND_ORIGIN` — your deployed frontend's URL (e.g.
     `https://hint-tutor.vercel.app`). Leave unset/`*` while testing.
5. Deploy. Render gives you a URL like `https://hint-tutor-api.onrender.com`
   — that's your `VITE_API_URL` for the frontend.

Railway works the same way and also reads the `Procfile`.

**Free-tier note:** Render's free web services spin down after inactivity,
so the first request after a while will be slow (~30-60s cold start).
