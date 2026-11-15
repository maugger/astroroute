"""Elementary two-body orbital mechanics utilities."""

import math


def circular_velocity(radius_m: float, mu_m3_s2: float) -> float:
    if (
        not math.isfinite(radius_m)
        or not math.isfinite(mu_m3_s2)
        or radius_m <= 0
        or mu_m3_s2 <= 0
    ):
        raise ValueError("radius and gravitational parameter must be positive")
    return math.sqrt(mu_m3_s2 / radius_m)


def vis_viva_velocity(radius_m: float, semi_major_axis_m: float, mu_m3_s2: float) -> float:
    if (
        not math.isfinite(radius_m)
        or not math.isfinite(semi_major_axis_m)
        or not math.isfinite(mu_m3_s2)
        or radius_m <= 0
        or semi_major_axis_m <= 0
        or mu_m3_s2 <= 0
    ):
        raise ValueError("radius, semi-major axis, and gravitational parameter must be positive")
    term = 2 / radius_m - 1 / semi_major_axis_m
    if term <= 0:
        raise ValueError("the requested state is not physically valid for this ellipse")
    return math.sqrt(mu_m3_s2 * term)
