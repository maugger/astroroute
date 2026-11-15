from astroroute.core.candidates import generate_candidates
from astroroute.core.constants import EARTH_RADIUS_M


def test_candidate_generation_always_includes_hohmann_baseline():
    candidates = generate_candidates(
        EARTH_RADIUS_M + 400_000,
        EARTH_RADIUS_M + 35_786_000,
        [EARTH_RADIUS_M + 80_000_000],
    )
    assert len(candidates) == 2
    assert candidates[0].route_id == "hohmann"
    assert candidates[1].route_type == "Bi-elliptic transfer"


def test_candidate_generation_can_run_without_bielliptic_samples():
    candidates = generate_candidates(
        EARTH_RADIUS_M + 400_000,
        EARTH_RADIUS_M + 35_786_000,
    )
    assert [candidate.route_id for candidate in candidates] == ["hohmann"]
