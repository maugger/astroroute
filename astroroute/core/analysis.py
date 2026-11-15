"""Backend orchestration for a complete AstroRoute mission analysis."""

from .candidates import generate_candidates
from .constraints import evaluate_candidates
from .models import Mission, MissionAnalysis
from .pareto import pareto_frontier
from .recommendation import recommend
from .sensitivity import run_sensitivity


def analyze_mission(mission: Mission) -> MissionAnalysis:
    """Generate, evaluate, compare, and recommend trajectory candidates."""

    candidates = generate_candidates(
        initial_radius_m=mission.initial_radius_m,
        target_radius_m=mission.target_radius_m,
        intermediate_apoapsis_radii_m=mission.intermediate_apoapsis_radii_m,
    )
    evaluations = evaluate_candidates(candidates, mission.constraints)
    feasible_evaluations = [
        evaluation for evaluation in evaluations if evaluation.feasible
    ]
    pareto_candidates = pareto_frontier(
        [evaluation.candidate for evaluation in feasible_evaluations]
    )
    pareto_route_ids = tuple(candidate.route_id for candidate in pareto_candidates)
    sensitivity_results = tuple(
        run_sensitivity(evaluation.candidate, mission.sensitivity)
        for evaluation in feasible_evaluations
    )
    sensitivity_by_route = {
        result.route_id: result for result in sensitivity_results
    }
    recommendation = recommend(
        candidates=feasible_evaluations,
        sensitivity_results=sensitivity_by_route,
        preferences=mission.preferences,
    )
    return MissionAnalysis(
        candidates=tuple(evaluations),
        pareto_route_ids=pareto_route_ids,
        sensitivity_results=sensitivity_results,
        recommendation=recommendation,
    )
