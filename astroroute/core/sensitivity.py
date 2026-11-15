"""Reproducible burn-magnitude sensitivity experiments."""

import math
import random
from collections.abc import Iterable

from .constants import EARTH_MU_M3_S2
from .models import SensitivityResult, SensitivitySettings, TransferResult
from .orbital import circular_velocity, vis_viva_velocity

State = tuple[float, float, float, float]


def _acceleration(state: State, mu_m3_s2: float) -> tuple[float, float]:
    x_m, y_m, _, _ = state
    radius_m = math.hypot(x_m, y_m)
    factor = -mu_m3_s2 / radius_m**3
    return factor * x_m, factor * y_m


def _derivative(state: State, mu_m3_s2: float) -> State:
    acceleration_x_m_s2, acceleration_y_m_s2 = _acceleration(state, mu_m3_s2)
    return state[2], state[3], acceleration_x_m_s2, acceleration_y_m_s2


def _add_scaled(state: State, derivative: State, scale: float) -> State:
    return (
        state[0] + scale * derivative[0],
        state[1] + scale * derivative[1],
        state[2] + scale * derivative[2],
        state[3] + scale * derivative[3],
    )


def _propagate(state: State, duration_s: float, mu_m3_s2: float) -> State:
    if duration_s < 0:
        raise ValueError("propagation duration cannot be negative")
    if duration_s == 0:
        return state

    steps = max(20, math.ceil(duration_s / 30))
    step_s = duration_s / steps
    current = state
    for _ in range(steps):
        k1 = _derivative(current, mu_m3_s2)
        k2 = _derivative(_add_scaled(current, k1, step_s / 2), mu_m3_s2)
        k3 = _derivative(_add_scaled(current, k2, step_s / 2), mu_m3_s2)
        k4 = _derivative(_add_scaled(current, k3, step_s), mu_m3_s2)
        current = (
            current[0] + step_s / 6 * (k1[0] + 2 * k2[0] + 2 * k3[0] + k4[0]),
            current[1] + step_s / 6 * (k1[1] + 2 * k2[1] + 2 * k3[1] + k4[1]),
            current[2] + step_s / 6 * (k1[2] + 2 * k2[2] + 2 * k3[2] + k4[2]),
            current[3] + step_s / 6 * (k1[3] + 2 * k2[3] + 2 * k3[3] + k4[3]),
        )
    return current


def _apply_tangential_burn(
    state: State,
    nominal_delta_v_m_s: float,
    error_fraction: float,
) -> State:
    x_m, y_m, velocity_x_m_s, velocity_y_m_s = state
    radius_m = math.hypot(x_m, y_m)
    tangent_x = -y_m / radius_m
    tangent_y = x_m / radius_m
    actual_delta_v_m_s = nominal_delta_v_m_s * (1 + error_fraction)
    return (
        x_m,
        y_m,
        velocity_x_m_s + tangent_x * actual_delta_v_m_s,
        velocity_y_m_s + tangent_y * actual_delta_v_m_s,
    )


def _transfer_segments(candidate: TransferResult, mu_m3_s2: float) -> list[tuple[float, float]]:
    if candidate.route_type == "Hohmann transfer":
        first_semi_major_axis_m = (
            candidate.initial_radius_m + candidate.target_radius_m
        ) / 2
        first_duration_s = math.pi * math.sqrt(first_semi_major_axis_m**3 / mu_m3_s2)
        return [
            (candidate.delta_v_1_m_s, first_duration_s),
            (candidate.delta_v_2_m_s, 0),
        ]
    if candidate.route_type == "Bi-elliptic transfer":
        if candidate.intermediate_apoapsis_m is None:
            raise ValueError("bi-elliptic candidate is missing its intermediate apoapsis")
        first_semi_major_axis_m = (
            candidate.initial_radius_m + candidate.intermediate_apoapsis_m
        ) / 2
        second_semi_major_axis_m = (
            candidate.target_radius_m + candidate.intermediate_apoapsis_m
        ) / 2
        first_duration_s = math.pi * math.sqrt(first_semi_major_axis_m**3 / mu_m3_s2)
        second_duration_s = math.pi * math.sqrt(second_semi_major_axis_m**3 / mu_m3_s2)
        return [
            (candidate.delta_v_1_m_s, first_duration_s),
            (candidate.delta_v_2_m_s, second_duration_s),
            (candidate.delta_v_3_m_s, 0),
        ]
    raise ValueError(f"unsupported trajectory type: {candidate.route_type}")


def _terminal_errors(
    candidate: TransferResult,
    error_fractions: Iterable[float],
    mu_m3_s2: float,
) -> tuple[float, float]:
    initial_speed_m_s = circular_velocity(candidate.initial_radius_m, mu_m3_s2)
    target_speed_m_s = circular_velocity(candidate.target_radius_m, mu_m3_s2)
    state: State = (candidate.initial_radius_m, 0, 0, initial_speed_m_s)
    segments = _transfer_segments(candidate, mu_m3_s2)

    for index, ((delta_v_m_s, duration_s), error_fraction) in enumerate(
        zip(segments, error_fractions)
    ):
        state = _apply_tangential_burn(state, delta_v_m_s, error_fraction)
        if index < len(segments) - 1:
            state = _propagate(state, duration_s, mu_m3_s2)

    terminal_radius_m = math.hypot(state[0], state[1])
    terminal_speed_m_s = math.hypot(state[2], state[3])
    return (
        abs(terminal_radius_m - candidate.target_radius_m),
        abs(terminal_speed_m_s - target_speed_m_s),
    )


def _percentile(values: list[float], percentile: float) -> float:
    ordered = sorted(values)
    position = (len(ordered) - 1) * percentile / 100
    lower_index = math.floor(position)
    upper_index = math.ceil(position)
    if lower_index == upper_index:
        return ordered[lower_index]
    fraction = position - lower_index
    return ordered[lower_index] + fraction * (
        ordered[upper_index] - ordered[lower_index]
    )


def run_sensitivity(
    candidate: TransferResult,
    settings: SensitivitySettings,
    mu_m3_s2: float = EARTH_MU_M3_S2,
) -> SensitivityResult:
    """Run a seeded Monte Carlo burn-magnitude sensitivity experiment."""

    if not math.isfinite(mu_m3_s2) or mu_m3_s2 <= 0:
        raise ValueError("gravitational parameter must be positive")
    random_generator = random.Random(settings.random_seed)
    segments = _transfer_segments(candidate, mu_m3_s2)
    radius_errors_m: list[float] = []
    speed_errors_m_s: list[float] = []

    for _ in range(settings.samples):
        errors = [
            random_generator.gauss(0, settings.burn_magnitude_error_std_fraction)
            for _ in segments
        ]
        radius_error_m, speed_error_m_s = _terminal_errors(
            candidate,
            errors,
            mu_m3_s2,
        )
        radius_errors_m.append(radius_error_m)
        speed_errors_m_s.append(speed_error_m_s)

    return SensitivityResult(
        route_id=candidate.route_id,
        samples=settings.samples,
        random_seed=settings.random_seed,
        burn_magnitude_error_std_fraction=settings.burn_magnitude_error_std_fraction,
        terminal_radius_error_median_m=_percentile(radius_errors_m, 50),
        terminal_radius_error_p95_m=_percentile(radius_errors_m, 95),
        terminal_radius_error_worst_m=max(radius_errors_m),
        terminal_speed_error_median_m_s=_percentile(speed_errors_m_s, 50),
        terminal_speed_error_p95_m_s=_percentile(speed_errors_m_s, 95),
        terminal_speed_error_worst_m_s=max(speed_errors_m_s),
    )
