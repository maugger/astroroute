from astroroute.core.models import TransferResult
from astroroute.core.pareto import pareto_frontier


def make_result(route_id: str, delta_v: float, duration: float) -> TransferResult:
    return TransferResult(
        route_id=route_id,
        route_type="test",
        initial_radius_m=7_000_000,
        target_radius_m=8_000_000,
        delta_v_1_m_s=delta_v,
        delta_v_2_m_s=0,
        delta_v_total_m_s=delta_v,
        transfer_time_s=duration,
    )


def test_pareto_frontier_removes_a_candidate_worse_on_every_objective():
    fast = make_result("fast", 1_200, 1_000)
    efficient = make_result("efficient", 900, 2_000)
    dominated = make_result("dominated", 1_300, 2_100)
    frontier = pareto_frontier([fast, efficient, dominated])
    assert [candidate.route_id for candidate in frontier] == ["fast", "efficient"]


def test_pareto_frontier_rejects_unknown_objective():
    result = make_result("route", 1_000, 1_000)
    try:
        pareto_frontier([result], ("unknown",))
    except ValueError as error:
        assert "unknown transfer objective" in str(error)
    else:
        raise AssertionError("unknown objective should raise ValueError")
