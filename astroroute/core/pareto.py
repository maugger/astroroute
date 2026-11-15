"""Pareto-frontier filtering for minimization objectives."""

from collections.abc import Sequence

from .models import TransferResult


def _dominates(
    left: TransferResult,
    right: TransferResult,
    objective_keys: tuple[str, ...],
) -> bool:
    left_values = [getattr(left, key) for key in objective_keys]
    right_values = [getattr(right, key) for key in objective_keys]
    no_worse = all(
        left_value <= right_value
        for left_value, right_value in zip(left_values, right_values)
    )
    strictly_better = any(
        left_value < right_value for left_value, right_value in zip(left_values, right_values)
    )
    return no_worse and strictly_better


def pareto_frontier(
    candidates: Sequence[TransferResult],
    objective_keys: tuple[str, ...] = ("delta_v_total_m_s", "transfer_time_s"),
) -> list[TransferResult]:
    """Return candidates not dominated across all selected minimization objectives."""

    if not objective_keys:
        raise ValueError("at least one objective is required")
    for candidate in candidates:
        for objective_key in objective_keys:
            if not hasattr(candidate, objective_key):
                raise ValueError(f"unknown transfer objective: {objective_key}")

    return [
        candidate
        for candidate in candidates
        if not any(
            other is not candidate and _dominates(other, candidate, objective_keys)
            for other in candidates
        )
    ]
