"""Mission-constraint evaluation for calculated trajectory candidates."""

from collections.abc import Sequence

from .models import CandidateEvaluation, MissionConstraints, TransferResult
from .propulsion import estimate_propellant


def evaluate_candidate(
    candidate: TransferResult,
    constraints: MissionConstraints,
) -> CandidateEvaluation:
    """Calculate fuel use and return transparent constraint results."""

    propellant = estimate_propellant(
        delta_v_m_s=candidate.delta_v_total_m_s,
        wet_mass_kg=constraints.wet_mass_kg,
        isp_s=constraints.specific_impulse_s,
    )
    rejection_reasons: list[str] = []

    if (
        constraints.max_propellant_mass_kg is not None
        and propellant.propellant_mass_kg > constraints.max_propellant_mass_kg
    ):
        rejection_reasons.append("propellant limit exceeded")
    if (
        constraints.max_transfer_time_s is not None
        and candidate.transfer_time_s > constraints.max_transfer_time_s
    ):
        rejection_reasons.append("maximum transfer duration exceeded")

    return CandidateEvaluation(
        candidate=candidate,
        propellant=propellant,
        feasible=not rejection_reasons,
        rejection_reasons=tuple(rejection_reasons),
    )


def evaluate_candidates(
    candidates: Sequence[TransferResult],
    constraints: MissionConstraints,
) -> list[CandidateEvaluation]:
    """Evaluate every candidate while retaining rejected candidates and reasons."""

    return [evaluate_candidate(candidate, constraints) for candidate in candidates]


def feasible_candidates(
    candidates: Sequence[TransferResult],
    constraints: MissionConstraints,
) -> list[CandidateEvaluation]:
    """Return only candidates that satisfy all supplied mission constraints."""

    return [
        evaluation
        for evaluation in evaluate_candidates(candidates, constraints)
        if evaluation.feasible
    ]
