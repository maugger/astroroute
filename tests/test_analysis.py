from astroroute.core.analysis import analyze_mission
from astroroute.core.constants import EARTH_RADIUS_M
from astroroute.core.models import (
    Mission,
    MissionConstraints,
    MissionPreferences,
    SensitivitySettings,
)


def make_mission(**constraint_updates):
    constraints = {
        "wet_mass_kg": 1_000,
        "specific_impulse_s": 320,
        "max_propellant_mass_kg": 1_000,
        "max_transfer_time_s": 1_000_000,
    }
    constraints.update(constraint_updates)
    return Mission(
        initial_radius_m=EARTH_RADIUS_M + 400_000,
        target_radius_m=EARTH_RADIUS_M + 2_000_000,
        constraints=MissionConstraints(**constraints),
        intermediate_apoapsis_radii_m=(EARTH_RADIUS_M + 10_000_000,),
        preferences=MissionPreferences(
            delta_v_weight=0.5,
            transfer_time_weight=0.25,
            sensitivity_weight=0.25,
        ),
        sensitivity=SensitivitySettings(samples=3, random_seed=4),
    )


def test_analysis_orchestrates_all_backend_steps():
    result = analyze_mission(make_mission())
    assert len(result.candidates) == 2
    assert len(result.sensitivity_results) == 2
    assert result.pareto_route_ids
    assert result.recommendation is not None
    assert result.recommendation.route_id in {"hohmann", result.candidates[1].candidate.route_id}


def test_analysis_returns_no_recommendation_when_all_candidates_are_infeasible():
    result = analyze_mission(make_mission(max_propellant_mass_kg=0.1))
    assert result.recommendation is None
    assert result.sensitivity_results == ()
    assert all(not candidate.feasible for candidate in result.candidates)
