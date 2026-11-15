"""Three-impulse bi-elliptic transfer calculations."""

import math

from .constants import EARTH_MU_M3_S2
from .models import TransferResult
from .orbital import circular_velocity, vis_viva_velocity
from .validation import validate_transfer_radii


def calculate_bielliptic(
    initial_radius_m: float,
    target_radius_m: float,
    intermediate_apoapsis_m: float,
    mu_m3_s2: float = EARTH_MU_M3_S2,
) -> TransferResult:
    validate_transfer_radii(initial_radius_m, target_radius_m)
    largest_endpoint = max(initial_radius_m, target_radius_m)
    if (
        not math.isfinite(intermediate_apoapsis_m)
        or intermediate_apoapsis_m <= largest_endpoint
    ):
        raise ValueError("intermediate apoapsis must exceed both endpoint radii")

    first_semi_major_axis = (initial_radius_m + intermediate_apoapsis_m) / 2
    second_semi_major_axis = (target_radius_m + intermediate_apoapsis_m) / 2
    initial_circular_v = circular_velocity(initial_radius_m, mu_m3_s2)
    target_circular_v = circular_velocity(target_radius_m, mu_m3_s2)

    first_periapsis_v = vis_viva_velocity(
        initial_radius_m, first_semi_major_axis, mu_m3_s2
    )
    first_apoapsis_v = vis_viva_velocity(
        intermediate_apoapsis_m, first_semi_major_axis, mu_m3_s2
    )
    second_apoapsis_v = vis_viva_velocity(
        intermediate_apoapsis_m, second_semi_major_axis, mu_m3_s2
    )
    second_periapsis_v = vis_viva_velocity(target_radius_m, second_semi_major_axis, mu_m3_s2)

    burn_1 = abs(first_periapsis_v - initial_circular_v)
    burn_2 = abs(second_apoapsis_v - first_apoapsis_v)
    burn_3 = abs(target_circular_v - second_periapsis_v)
    time_1 = math.pi * math.sqrt(first_semi_major_axis**3 / mu_m3_s2)
    time_2 = math.pi * math.sqrt(second_semi_major_axis**3 / mu_m3_s2)
    return TransferResult(
        route_id=f"bielliptic-{intermediate_apoapsis_m:.0f}m",
        route_type="Bi-elliptic transfer",
        initial_radius_m=initial_radius_m,
        target_radius_m=target_radius_m,
        delta_v_1_m_s=burn_1,
        delta_v_2_m_s=burn_2,
        delta_v_3_m_s=burn_3,
        delta_v_total_m_s=burn_1 + burn_2 + burn_3,
        transfer_time_s=time_1 + time_2,
        intermediate_apoapsis_m=intermediate_apoapsis_m,
    )
