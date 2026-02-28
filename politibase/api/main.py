"""FastAPI application for Politibase.

Run with:
    uvicorn politibase.api.main:app --reload
"""

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pathlib import Path

from politibase.api.routes import candidates, elections, jurisdictions, ballot
from politibase.api import pages
from politibase.db.database import init_db

app = FastAPI(
    title="Politibase",
    description="Local election candidate research platform for the Fargo-Moorhead metro area",
    version="0.1.0",
)

# Static files and templates for the frontend
_frontend_dir = Path(__file__).resolve().parent.parent.parent / "frontend"
app.mount("/static", StaticFiles(directory=str(_frontend_dir / "static")), name="static")
templates = Jinja2Templates(directory=str(_frontend_dir / "templates"))

# Register API routes
app.include_router(jurisdictions.router, prefix="/api/jurisdictions", tags=["Jurisdictions"])
app.include_router(candidates.router, prefix="/api/candidates", tags=["Candidates"])
app.include_router(elections.router, prefix="/api/elections", tags=["Elections"])
app.include_router(ballot.router, prefix="/api/ballot", tags=["Ballot Lookup"])

# Register page routes (server-rendered HTML)
# These must come AFTER the /static mount and AFTER /api routes
app.include_router(pages.router, tags=["Pages"])


@app.on_event("startup")
def on_startup():
    init_db()


@app.get("/api/health")
def health():
    return {"status": "ok", "version": "0.1.0"}
