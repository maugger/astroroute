"""Ideal rocket-equation calculations."""

import math

from .constants import STANDARD_GRAVITY_M_S2
from .models import PropellantResult
from .validation import validate_propulsion_inputs


def estimate_propellant(
    delta_v_m_s: float,
    wet_mass_kg: float,
    isp_s: float,
    g0_m_s2: float = STANDARD_GRAVITY_M_S2,
) -> PropellantResult:
    if not math.isfinite(delta_v_m_s) or delta_v_m_s < 0:
        raise ValueError("delta-v cannot be negative")
    if not math.isfinite(g0_m_s2) or g0_m_s2 <= 0:
        raise ValueError("standard gravity must be positive")
    validate_propulsion_inputs(wet_mass_kg, isp_s)
    mass_ratio = math.exp(delta_v_m_s / (isp_s * g0_m_s2))
    final_mass = wet_mass_kg / mass_ratio
    return PropellantResult(
        initial_mass_kg=wet_mass_kg,
        final_mass_kg=final_mass,
        propellant_mass_kg=wet_mass_kg - final_mass,
        mass_ratio=mass_ratio,
    )
