"""Typed data models shared by the calculation engine."""

from pydantic import BaseModel, ConfigDict, Field


class TransferResult(BaseModel):
    model_config = ConfigDict(frozen=True)

    route_id: str
    route_type: str
    initial_radius_m: float = Field(gt=0)
    target_radius_m: float = Field(gt=0)
    delta_v_1_m_s: float = Field(ge=0)
    delta_v_2_m_s: float = Field(ge=0)
    delta_v_3_m_s: float = Field(default=0, ge=0)
    delta_v_total_m_s: float = Field(ge=0)
    transfer_time_s: float = Field(ge=0)
    intermediate_apoapsis_m: float | None = Field(default=None, gt=0)


class PropellantResult(BaseModel):
    model_config = ConfigDict(frozen=True)

    initial_mass_kg: float = Field(gt=0)
    final_mass_kg: float = Field(gt=0)
    propellant_mass_kg: float = Field(ge=0)
    mass_ratio: float = Field(ge=1)


class MissionConstraints(BaseModel):
    model_config = ConfigDict(frozen=True)

    wet_mass_kg: float = Field(gt=0)
    specific_impulse_s: float = Field(gt=0)
    max_propellant_mass_kg: float | None = Field(default=None, gt=0)
    max_transfer_time_s: float | None = Field(default=None, gt=0)


class CandidateEvaluation(BaseModel):
    model_config = ConfigDict(frozen=True)

    candidate: TransferResult
    propellant: PropellantResult
    feasible: bool
    rejection_reasons: tuple[str, ...] = ()


class SensitivitySettings(BaseModel):
    model_config = ConfigDict(frozen=True)

    samples: int = Field(default=200, ge=1, le=10_000)
    burn_magnitude_error_std_fraction: float = Field(default=0.001, ge=0)
    random_seed: int = 42


class SensitivityResult(BaseModel):
    model_config = ConfigDict(frozen=True)

    route_id: str
    samples: int
    random_seed: int
    burn_magnitude_error_std_fraction: float
    terminal_radius_error_median_m: float = Field(ge=0)
    terminal_radius_error_p95_m: float = Field(ge=0)
    terminal_radius_error_worst_m: float = Field(ge=0)
    terminal_speed_error_median_m_s: float = Field(ge=0)
    terminal_speed_error_p95_m_s: float = Field(ge=0)
    terminal_speed_error_worst_m_s: float = Field(ge=0)
