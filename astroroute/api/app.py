"""FastAPI application for AstroRoute mission analysis."""

from fastapi import FastAPI, HTTPException

from astroroute.core.analysis import analyze_mission
from astroroute.core.models import Mission, MissionAnalysis

app = FastAPI(
    title="AstroRoute API",
    version="0.1.0",
    description="Explainable circular-orbit transfer analysis.",
)


@app.get(
    "/health",
    tags=["system"],
    summary="Check API availability",
)
def health_check() -> dict[str, str]:
    """Report whether the API process is available."""

    return {"status": "ok"}


@app.post(
    "/api/v1/missions/analyze",
    response_model=MissionAnalysis,
    tags=["missions"],
    summary="Analyze a circular-orbit mission",
    response_description=(
        "Candidate evaluations, Pareto routes, sensitivity results, and recommendation"
    ),
)
def analyze_mission_endpoint(mission: Mission) -> MissionAnalysis:
    """Run the backend mission analysis for a validated mission request."""

    try:
        return analyze_mission(mission)
    except ValueError as error:
        raise HTTPException(status_code=422, detail=str(error)) from error
