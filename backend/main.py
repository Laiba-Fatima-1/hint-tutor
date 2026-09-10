import os

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from agent_core import run_agent, AgentError

app = FastAPI(title="Hint, Don't Solve — Tutor API")

# Comma-separated list of allowed origins, e.g. "https://your-app.vercel.app,http://localhost:5173"
_origins_env = os.environ.get("FRONTEND_ORIGIN", "*")
allow_origins = [o.strip() for o in _origins_env.split(",")] if _origins_env != "*" else ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allow_origins,
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


class TutorRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=4000)
    code: str | None = Field(default=None, max_length=8000)


class TutorResponse(BaseModel):
    category: str
    policy: str
    policy_label: str
    policy_color: str
    response: str


@app.get("/api/health")
def health():
    return {"status": "ok", "gemini_key_configured": bool(os.environ.get("GEMINI_API_KEY"))}


@app.post("/api/tutor", response_model=TutorResponse)
def tutor(req: TutorRequest):
    try:
        result = run_agent(req.message, req.code)
    except AgentError as exc:
        raise HTTPException(status_code=502, detail=str(exc))
    return result
