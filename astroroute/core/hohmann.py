"""Analytic two-impulse Hohmann transfer calculations."""

import math

from .constants import EARTH_MU_M3_S2
from .models import TransferResult
from .orbital import circular_velocity, vis_viva_velocity
from .validation import validate_transfer_radii


def calculate_hohmann(
    initial_radius_m: float,
    target_radius_m: float,
    mu_m3_s2: float = EARTH_MU_M3_S2,
) -> TransferResult:
    validate_transfer_radii(initial_radius_m, target_radius_m)
    semi_major_axis_m = (initial_radius_m + target_radius_m) / 2
    initial_circular_v = circular_velocity(initial_radius_m, mu_m3_s2)
    target_circular_v = circular_velocity(target_radius_m, mu_m3_s2)
    transfer_initial_v = vis_viva_velocity(initial_radius_m, semi_major_axis_m, mu_m3_s2)
    transfer_target_v = vis_viva_velocity(target_radius_m, semi_major_axis_m, mu_m3_s2)
    first_burn = abs(transfer_initial_v - initial_circular_v)
    second_burn = abs(target_circular_v - transfer_target_v)
    transfer_time_s = math.pi * math.sqrt(semi_major_axis_m**3 / mu_m3_s2)
    return TransferResult(
        route_id="hohmann",
        route_type="Hohmann transfer",
        initial_radius_m=initial_radius_m,
        target_radius_m=target_radius_m,
        delta_v_1_m_s=first_burn,
        delta_v_2_m_s=second_burn,
        delta_v_total_m_s=first_burn + second_burn,
        transfer_time_s=transfer_time_s,
    )
