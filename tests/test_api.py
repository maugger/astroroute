from fastapi import HTTPException

from astroroute.api.app import analyze_mission_endpoint, app, health_check
from astroroute.core.constants import EARTH_RADIUS_M
from astroroute.core.models import Mission


def make_payload(**updates):
    payload = {
        "initial_radius_m": EARTH_RADIUS_M + 400_000,
        "target_radius_m": EARTH_RADIUS_M + 2_000_000,
        "constraints": {
            "wet_mass_kg": 1_000,
            "specific_impulse_s": 320,
            "max_propellant_mass_kg": 1_000,
            "max_transfer_time_s": 1_000_000,
        },
        "intermediate_apoapsis_radii_m": [EARTH_RADIUS_M + 10_000_000],
        "sensitivity": {
            "samples": 3,
            "random_seed": 4,
        },
    }
    payload.update(updates)
    return payload


def test_health_endpoint_reports_api_availability():
    assert health_check() == {"status": "ok"}
    health_schema = app.openapi()["paths"]["/health"]["get"]

    assert health_schema["summary"] == "Check API availability"


def test_analysis_endpoint_returns_backend_result():
    result = analyze_mission_endpoint(Mission.model_validate(make_payload()))
    analysis_schema = app.openapi()["paths"]["/api/v1/missions/analyze"]["post"]

    assert len(result.candidates) == 2
    assert result.recommendation is not None
    assert analysis_schema["summary"] == "Analyze a circular-orbit mission"
    assert analysis_schema["requestBody"]["required"] is True


def test_analysis_endpoint_rejects_physically_invalid_transfer():
    payload = make_payload(
        initial_radius_m=EARTH_RADIUS_M,
    )

    try:
        analyze_mission_endpoint(Mission.model_validate(payload))
    except HTTPException as error:
        assert error.status_code == 422
    else:
        raise AssertionError("physically invalid mission was accepted")
