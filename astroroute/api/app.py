"""FastAPI application for AstroRoute mission analysis."""

from fastapi import FastAPI, HTTPException

from astroroute.core.analysis import analyze_mission
from astroroute.core.models import Mission, MissionAnalysis

app = FastAPI(
    title="AstroRoute API",
    version="0.1.0",
    description="Explainable circular-orbit transfer analysis.",
)


@app.get("/health")
def health_check() -> dict[str, str]:
    """Report whether the API process is available."""

    return {"status": "ok"}


@app.post("/api/v1/missions/analyze", response_model=MissionAnalysis)
def analyze_mission_endpoint(mission: Mission) -> MissionAnalysis:
    """Run the backend mission analysis for a validated mission request."""

    try:
        return analyze_mission(mission)
    except ValueError as error:
        raise HTTPException(status_code=422, detail=str(error)) from error
