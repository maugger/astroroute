export type MissionAnalysis = {
  candidates: CandidateEvaluation[];
  pareto_route_ids: string[];
  sensitivity_results: SensitivityResult[];
  recommendation: Recommendation | null;
};

export type CandidateEvaluation = {
  candidate: {
    route_id: string;
    route_type: string;
    delta_v_total_m_s: number;
    transfer_time_s: number;
  };
  propellant: {
    propellant_mass_kg: number;
  };
  feasible: boolean;
  rejection_reasons: string[];
};

export type SensitivityResult = {
  route_id: string;
  terminal_radius_error_p95_m: number;
  terminal_speed_error_p95_m_s: number;
};

export type Recommendation = {
  route_id: string;
  weighted_score: number;
  explanation: string[];
};

export type MissionRequest = {
  initial_radius_m: number;
  target_radius_m: number;
  constraints: {
    wet_mass_kg: number;
    specific_impulse_s: number;
    max_propellant_mass_kg: number | null;
    max_transfer_time_s: number | null;
  };
  intermediate_apoapsis_radii_m: number[];
};

const apiBaseUrl = import.meta.env.VITE_API_BASE_URL ?? "";

export async function analyzeMission(request: MissionRequest): Promise<MissionAnalysis> {
  const response = await fetch(`${apiBaseUrl}/api/v1/missions/analyze`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(request),
  });

  if (!response.ok) {
    const payload = (await response.json()) as { detail?: string };
    throw new Error(payload.detail ?? "Mission analysis failed.");
  }

  return (await response.json()) as MissionAnalysis;
}
