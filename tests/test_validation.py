import math

import pytest

from astroroute.core.constants import EARTH_MU_M3_S2, EARTH_RADIUS_M
from astroroute.core.orbital import circular_velocity
from astroroute.core.validation import validate_orbit_radius


def test_nan_orbit_radius_is_rejected():
    with pytest.raises(ValueError):
        validate_orbit_radius(math.nan)


def test_infinite_gravitational_parameter_is_rejected():
    with pytest.raises(ValueError):
        circular_velocity(EARTH_RADIUS_M + 400_000, math.inf)


def test_valid_orbit_radius_is_accepted():
    validate_orbit_radius(EARTH_RADIUS_M + 400_000)
    assert EARTH_MU_M3_S2 > 0
