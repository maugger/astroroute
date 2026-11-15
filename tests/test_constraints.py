import pytest

from astroroute.core.constraints import (
    evaluate_candidate,
    evaluate_candidates,
    feasible_candidates,
)
from astroroute.core.hohmann import calculate_hohmann
from astroroute.core.constants import EARTH_RADIUS_M
from astroroute.core.models import MissionConstraints


@pytest.fixture
def hohmann_result():
    return calculate_hohmann(
        EARTH_RADIUS_M + 400_000,
        EARTH_RADIUS_M + 2_000_000,
    )


def test_propellant_limit_rejects_candidate(hohmann_result):
    constraints = MissionConstraints(
        wet_mass_kg=1_000,
        specific_impulse_s=320,
        max_propellant_mass_kg=1,
    )
    evaluation = evaluate_candidate(hohmann_result, constraints)
    assert not evaluation.feasible
    assert "propellant limit exceeded" in evaluation.rejection_reasons


def test_duration_limit_rejects_candidate(hohmann_result):
    constraints = MissionConstraints(
        wet_mass_kg=1_000,
        specific_impulse_s=320,
        max_transfer_time_s=1,
    )
    evaluation = evaluate_candidate(hohmann_result, constraints)
    assert not evaluation.feasible
    assert "maximum transfer duration exceeded" in evaluation.rejection_reasons


def test_candidate_must_satisfy_all_limits(hohmann_result):
    constraints = MissionConstraints(
        wet_mass_kg=1_000,
        specific_impulse_s=320,
        max_propellant_mass_kg=1,
        max_transfer_time_s=1,
    )
    evaluation = evaluate_candidate(hohmann_result, constraints)
    assert evaluation.rejection_reasons == (
        "propellant limit exceeded",
        "maximum transfer duration exceeded",
    )


def test_feasible_candidates_returns_only_accepted_routes(hohmann_result):
    constraints = MissionConstraints(
        wet_mass_kg=1_000,
        specific_impulse_s=320,
        max_propellant_mass_kg=1_000,
        max_transfer_time_s=hohmann_result.transfer_time_s + 1,
    )
    accepted = feasible_candidates([hohmann_result], constraints)
    assert len(accepted) == 1
    assert accepted[0].candidate.route_id == "hohmann"


def test_evaluate_candidates_preserves_rejected_results(hohmann_result):
    constraints = MissionConstraints(
        wet_mass_kg=1_000,
        specific_impulse_s=320,
        max_transfer_time_s=1,
    )
    evaluations = evaluate_candidates([hohmann_result], constraints)
    assert len(evaluations) == 1
    assert evaluations[0].candidate.route_id == "hohmann"
    assert not evaluations[0].feasible


def test_constraint_limits_must_be_positive():
    with pytest.raises(ValueError):
        MissionConstraints(
            wet_mass_kg=1_000,
            specific_impulse_s=320,
            max_propellant_mass_kg=0,
        )
