import pytest

from astroroute.core.propulsion import estimate_propellant


def test_zero_delta_v_uses_no_propellant():
    result = estimate_propellant(0, 1_000, 320)
    assert result.propellant_mass_kg == pytest.approx(0)
    assert result.final_mass_kg == pytest.approx(1_000)
    assert result.mass_ratio == pytest.approx(1)


def test_propellant_increases_with_delta_v():
    low = estimate_propellant(500, 1_000, 320)
    high = estimate_propellant(1_000, 1_000, 320)
    assert high.propellant_mass_kg > low.propellant_mass_kg


def test_propulsion_inputs_are_validated():
    with pytest.raises(ValueError, match="specific impulse"):
        estimate_propellant(100, 1_000, 0)
