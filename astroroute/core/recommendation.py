"""Transparent weighted recommendation for feasible mission candidates."""

from collections.abc import Mapping, Sequence

from .models import (
    CandidateEvaluation,
    MissionPreferences,
    Recommendation,
    SensitivityResult,
)


def _normalise(value: float, values: Sequence[float]) -> float:
    minimum = min(values)
    maximum = max(values)
    if maximum == minimum:
        return 0.0
    return (value - minimum) / (maximum - minimum)


def recommend(
    candidates: Sequence[CandidateEvaluation],
    sensitivity_results: Mapping[str, SensitivityResult],
    preferences: MissionPreferences,
) -> Recommendation | None:
    """Select the lowest weighted score among feasible candidates."""

    if not candidates:
        return None
    missing_results = [
        candidate.candidate.route_id
        for candidate in candidates
        if candidate.candidate.route_id not in sensitivity_results
    ]
    if missing_results:
        raise ValueError(
            "missing sensitivity results for: "
            + ", ".join(missing_results)
        )

    delta_v_values = [
        candidate.candidate.delta_v_total_m_s for candidate in candidates
    ]
    transfer_time_values = [
        candidate.candidate.transfer_time_s for candidate in candidates
    ]
    sensitivity_values = [
        sensitivity_results[candidate.candidate.route_id].terminal_radius_error_p95_m
        for candidate in candidates
    ]
    total_weight = (
        preferences.delta_v_weight
        + preferences.transfer_time_weight
        + preferences.sensitivity_weight
    )

    scored_candidates = []
    for candidate in candidates:
        route_id = candidate.candidate.route_id
        sensitivity = sensitivity_results[route_id]
        score = (
            preferences.delta_v_weight
            * _normalise(candidate.candidate.delta_v_total_m_s, delta_v_values)
            + preferences.transfer_time_weight
            * _normalise(candidate.candidate.transfer_time_s, transfer_time_values)
            + preferences.sensitivity_weight
            * _normalise(
                sensitivity.terminal_radius_error_p95_m,
                sensitivity_values,
            )
        ) / total_weight
        scored_candidates.append((score, candidate, sensitivity))

    best_score, best_candidate, best_sensitivity = min(
        scored_candidates,
        key=lambda item: (item[0], item[1].candidate.route_id),
    )
    return Recommendation(
        route_id=best_candidate.candidate.route_id,
        weighted_score=best_score,
        explanation=(
            f"Selected from {len(candidates)} feasible candidate(s).",
            "Lower delta-v, transfer time, and sensitivity error are preferred.",
            (
                f"{best_candidate.candidate.route_id} has "
                f"{best_candidate.candidate.delta_v_total_m_s:.2f} m/s delta-v, "
                f"{best_candidate.candidate.transfer_time_s:.2f} s transfer time, "
                f"and {best_sensitivity.terminal_radius_error_p95_m:.2f} m "
                "95th-percentile radius error."
            ),
        ),
    )
