"""FastAPI application for AstroRoute mission analysis."""

from typing import Any

from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from astroroute.core.analysis import analyze_mission
from astroroute.core.models import Mission, MissionAnalysis


class ErrorResponse(BaseModel):
    """Consistent error payload returned by the API."""

    detail: str
    errors: list[dict[str, Any]] = Field(default_factory=list)


app = FastAPI(
    title="AstroRoute API",
    version="0.1.0",
    description="Explainable circular-orbit transfer analysis.",
)

@app.exception_handler(RequestValidationError)
async def request_validation_exception_handler(
    request: Request,
    error: RequestValidationError,
) -> JSONResponse:
    """Return structured details when a request cannot be parsed or validated."""

    return JSONResponse(
        status_code=422,
        content=ErrorResponse(
            detail="request validation failed",
            errors=error.errors(),
        ).model_dump(),
    )


@app.exception_handler(HTTPException)
async def http_exception_handler(
    request: Request,
    error: HTTPException,
) -> JSONResponse:
    """Return the same error shape for endpoint-level validation failures."""

    return JSONResponse(
        status_code=error.status_code,
        content=ErrorResponse(detail=str(error.detail)).model_dump(),
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
    responses={422: {"model": ErrorResponse}},
)
def analyze_mission_endpoint(mission: Mission) -> MissionAnalysis:
    """Run the backend mission analysis for a validated mission request."""

    try:
        return analyze_mission(mission)
    except ValueError as error:
        raise HTTPException(status_code=422, detail=str(error)) from error
