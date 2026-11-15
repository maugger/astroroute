import math

import pytest

from astroroute.core.bielliptic import calculate_bielliptic
from astroroute.core.constants import EARTH_RADIUS_M


def test_bielliptic_transfer_has_positive_cost_and_duration():
    result = calculate_bielliptic(
        EARTH_RADIUS_M + 400_000,
        EARTH_RADIUS_M + 35_786_000,
        EARTH_RADIUS_M + 80_000_000,
    )
    assert result.route_type == "Bi-elliptic transfer"
    assert result.delta_v_total_m_s > 0
    assert result.delta_v_3_m_s > 0
    assert result.transfer_time_s > 0


def test_bielliptic_requires_apoapsis_above_endpoints():
    with pytest.raises(ValueError, match="intermediate apoapsis"):
        calculate_bielliptic(
            EARTH_RADIUS_M + 400_000,
            EARTH_RADIUS_M + 2_000_000,
            EARTH_RADIUS_M + 1_000_000,
        )


def test_bielliptic_rejects_non_finite_apoapsis():
    with pytest.raises(ValueError, match="intermediate apoapsis"):
        calculate_bielliptic(
            EARTH_RADIUS_M + 400_000,
            EARTH_RADIUS_M + 2_000_000,
            math.nan,
        )
