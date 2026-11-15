import math

import pytest

from astroroute.core.constants import EARTH_MU_M3_S2
from astroroute.core.orbital import circular_velocity, vis_viva_velocity


def test_circular_velocity_matches_definition():
    radius = 7_000_000.0
    assert circular_velocity(radius, EARTH_MU_M3_S2) == pytest.approx(
        math.sqrt(EARTH_MU_M3_S2 / radius)
    )


def test_vis_viva_for_circular_orbit_reduces_to_circular_velocity():
    radius = 7_000_000.0
    assert vis_viva_velocity(radius, radius, EARTH_MU_M3_S2) == pytest.approx(
        circular_velocity(radius, EARTH_MU_M3_S2)
    )


def test_orbital_inputs_must_be_positive():
    with pytest.raises(ValueError):
        circular_velocity(0, EARTH_MU_M3_S2)
