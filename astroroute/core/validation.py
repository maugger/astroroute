"""Physical input validation for the baseline two-body model."""

import math

from .constants import EARTH_RADIUS_M


def validate_orbit_radius(radius_m: float, *, name: str = "orbit radius") -> None:
    if not math.isfinite(radius_m) or radius_m <= EARTH_RADIUS_M:
        raise ValueError(f"{name} must be greater than Earth's radius")


def validate_transfer_radii(initial_radius_m: float, target_radius_m: float) -> None:
    validate_orbit_radius(initial_radius_m, name="initial orbit radius")
    validate_orbit_radius(target_radius_m, name="target orbit radius")
    if initial_radius_m == target_radius_m:
        raise ValueError("initial and target orbit radii must differ")


def validate_propulsion_inputs(wet_mass_kg: float, isp_s: float) -> None:
    if not math.isfinite(wet_mass_kg) or wet_mass_kg <= 0:
        raise ValueError("wet mass must be positive")
    if not math.isfinite(isp_s) or isp_s <= 0:
        raise ValueError("specific impulse must be positive")
