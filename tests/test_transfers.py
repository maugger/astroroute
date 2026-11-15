import pytest

from astroroute.core.constants import EARTH_MU_M3_S2, EARTH_RADIUS_M
from astroroute.core.hohmann import calculate_hohmann


def test_hohmann_result_is_positive_and_typed():
    result = calculate_hohmann(EARTH_RADIUS_M + 400_000, EARTH_RADIUS_M + 35_786_000)
    assert result.route_id == "hohmann"
    assert result.delta_v_total_m_s > 0
    assert result.transfer_time_s > 0
    assert result.delta_v_total_m_s == pytest.approx(
        result.delta_v_1_m_s + result.delta_v_2_m_s
    )


def test_hohmann_is_rejected_for_invalid_orbits():
    with pytest.raises(ValueError, match="Earth's radius"):
        calculate_hohmann(EARTH_RADIUS_M, EARTH_RADIUS_M + 1_000_000)


def test_higher_target_orbit_requires_positive_second_burn():
    result = calculate_hohmann(EARTH_RADIUS_M + 400_000, EARTH_RADIUS_M + 2_000_000)
    assert result.delta_v_1_m_s > 0
    assert result.delta_v_2_m_s > 0
    assert EARTH_MU_M3_S2 > 0
