"""Generate valid trajectory candidates for a circular-orbit mission."""

from collections.abc import Iterable

from .bielliptic import calculate_bielliptic
from .constants import EARTH_MU_M3_S2
from .hohmann import calculate_hohmann
from .models import TransferResult


def generate_candidates(
    initial_radius_m: float,
    target_radius_m: float,
    intermediate_apoapsis_radii_m: Iterable[float] = (),
    mu_m3_s2: float = EARTH_MU_M3_S2,
) -> list[TransferResult]:
    """Return the Hohmann baseline and valid sampled bi-elliptic routes."""

    candidates = [
        calculate_hohmann(
            initial_radius_m=initial_radius_m,
            target_radius_m=target_radius_m,
            mu_m3_s2=mu_m3_s2,
        )
    ]
    for intermediate_radius_m in intermediate_apoapsis_radii_m:
        candidates.append(
            calculate_bielliptic(
                initial_radius_m=initial_radius_m,
                target_radius_m=target_radius_m,
                intermediate_apoapsis_m=intermediate_radius_m,
                mu_m3_s2=mu_m3_s2,
            )
        )
    return candidates
