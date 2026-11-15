import pytest

from astroroute.core.bielliptic import calculate_bielliptic
from astroroute.core.constants import EARTH_RADIUS_M
from astroroute.core.hohmann import calculate_hohmann
from astroroute.core.models import SensitivitySettings
from astroroute.core.sensitivity import run_sensitivity


@pytest.fixture
def hohmann_result():
    return calculate_hohmann(
        EARTH_RADIUS_M + 400_000,
        EARTH_RADIUS_M + 2_000_000,
    )


def test_zero_burn_error_has_small_terminal_errors(hohmann_result):
    result = run_sensitivity(
        hohmann_result,
        SensitivitySettings(samples=5, burn_magnitude_error_std_fraction=0),
    )
    assert result.terminal_radius_error_worst_m < 1
    assert result.terminal_speed_error_worst_m_s < 0.001


def test_sensitivity_is_reproducible(hohmann_result):
    settings = SensitivitySettings(samples=20, random_seed=7)
    first = run_sensitivity(hohmann_result, settings)
    second = run_sensitivity(hohmann_result, settings)
    assert first == second


def test_nonzero_burn_error_produces_nonzero_sensitivity(hohmann_result):
    result = run_sensitivity(
        hohmann_result,
        SensitivitySettings(
            samples=20,
            burn_magnitude_error_std_fraction=0.01,
            random_seed=7,
        ),
    )
    assert result.terminal_radius_error_p95_m > 0
    assert result.terminal_speed_error_p95_m_s > 0


def test_bielliptic_sensitivity_is_supported():
    candidate = calculate_bielliptic(
        EARTH_RADIUS_M + 400_000,
        EARTH_RADIUS_M + 35_786_000,
        EARTH_RADIUS_M + 80_000_000,
    )
    result = run_sensitivity(
        candidate,
        SensitivitySettings(samples=3, burn_magnitude_error_std_fraction=0),
    )
    assert result.route_id == candidate.route_id
    assert result.samples == 3


def test_unsupported_route_type_is_rejected(hohmann_result):
    invalid_candidate = hohmann_result.model_copy(update={"route_type": "unknown"})
    with pytest.raises(ValueError, match="unsupported trajectory type"):
        run_sensitivity(invalid_candidate, SensitivitySettings(samples=1))
