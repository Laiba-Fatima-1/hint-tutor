# Frontend — Hint, Don't Solve

A Vite + React chat interface for the tutor agent. No Tailwind/UI kit — the
chalkboard styling is plain CSS in `src/App.css`, driven by the color tokens
in `src/index.css`.

## Run locally

```bash
npm install
cp .env.example .env      # set VITE_API_URL to your backend, e.g. http://localhost:8000
npm run dev
```

## Deploy to Vercel

1. Push this `frontend/` folder to a GitHub repo (or the monorepo root — see
   below).
2. In Vercel: **New Project** → import the repo.
3. If this lives inside a monorepo alongside `backend/`, set **Root
   Directory** to `frontend`.
4. Framework preset: Vite (auto-detected). Build command `npm run build`,
   output directory `dist` (defaults are correct).
5. Add an environment variable:
   - `VITE_API_URL` = the URL of your deployed backend (e.g.
     `https://hint-tutor-api.onrender.com`)
6. Deploy.

Any static host works the same way (Netlify, Cloudflare Pages, GitHub
Pages) — build with `npm run build` and serve `dist/`.
