import { useState, type FormEvent } from "react";
import {
  analyzeMission,
  type CandidateEvaluation,
  type MissionAnalysis,
  type MissionRequest,
  type TransferResult,
} from "./api";

const EARTH_RADIUS_M = 6_378_137;
const initialMission: MissionRequest = {
  initial_radius_m: 6_778_137,
  target_radius_m: 8_378_137,
  constraints: {
    wet_mass_kg: 1_000,
    specific_impulse_s: 320,
    max_propellant_mass_kg: 1_000,
    max_transfer_time_s: 1_000_000,
  },
  intermediate_apoapsis_radii_m: [16_378_137],
};

function formatNumber(value: number, digits = 0): string {
  return new Intl.NumberFormat("en-US", { maximumFractionDigits: digits }).format(value);
}

function transferPath(candidate: TransferResult, center: number, scale: number): string {
  const firstRadiusM = Math.min(candidate.initial_radius_m, candidate.target_radius_m);
  const finalRadiusM = Math.max(candidate.initial_radius_m, candidate.target_radius_m);
  const waypoints = candidate.intermediate_apoapsis_m
    ? [firstRadiusM, candidate.intermediate_apoapsis_m, finalRadiusM]
    : [firstRadiusM, finalRadiusM];
  const segments = waypoints.slice(0, -1).map((periapsisM, index) => {
    const apoapsisM = waypoints[index + 1];
    const semiMajorAxisM = (periapsisM + apoapsisM) / 2;
    const semiMinorAxisM = Math.sqrt(periapsisM * apoapsisM);
    const focusOffsetM = semiMajorAxisM - periapsisM;
    const points = Array.from({ length: 65 }, (_, pointIndex) => {
      const eccentricAnomalyRad = (Math.PI * pointIndex) / 64;
      const xM = semiMajorAxisM * Math.cos(eccentricAnomalyRad) - focusOffsetM;
      const yM = semiMinorAxisM * Math.sin(eccentricAnomalyRad);
      return `${center + xM * scale},${center - yM * scale}`;
    });
    return points.join(" ");
  });
  return segments.join(" ");
}

function OrbitDiagram({ candidate }: { candidate: TransferResult }) {
  const size = 620;
  const center = size / 2;
  const maxRadiusM = Math.max(
    candidate.initial_radius_m,
    candidate.target_radius_m,
    candidate.intermediate_apoapsis_m ?? 0,
  );
  const scale = (size * 0.44) / maxRadiusM;
  const transferPoints = transferPath(candidate, center, scale);
  const initialOrbitRadiusPx = candidate.initial_radius_m * scale;
  const targetOrbitRadiusPx = candidate.target_radius_m * scale;
  const earthRadiusPx = EARTH_RADIUS_M * scale;
  const burnPoints = candidate.intermediate_apoapsis_m
    ? [candidate.initial_radius_m, candidate.intermediate_apoapsis_m, candidate.target_radius_m]
    : [candidate.initial_radius_m, candidate.target_radius_m];

  return (
    <svg className="orbit-diagram" viewBox={`0 0 ${size} ${size}`} role="img" aria-label={`${candidate.route_type} orbital transfer diagram`}>
      <circle className="orbit-ring initial-orbit" cx={center} cy={center} r={initialOrbitRadiusPx} />
      <circle className="orbit-ring target-orbit" cx={center} cy={center} r={targetOrbitRadiusPx} />
      <polyline className="transfer-arc" points={transferPoints} />
      {burnPoints.map((radiusM, index) => (
        <circle
          className="maneuver-marker"
          cx={center + radiusM * scale}
          cy={center}
          key={`${radiusM}-${index}`}
          r="4"
        />
      ))}
      <circle className="earth-disc" cx={center} cy={center} r={earthRadiusPx} />
    </svg>
  );
}

function ParetoPlot({
  candidates,
  paretoRouteIds,
  selectedRouteId,
  onSelect,
}: {
  candidates: CandidateEvaluation[];
  paretoRouteIds: string[];
  selectedRouteId: string;
  onSelect: (routeId: string) => void;
}) {
  const width = 1000;
  const height = 480;
  const plot = { left: 86, right: 36, top: 34, bottom: 70 };
  const plotWidth = width - plot.left - plot.right;
  const plotHeight = height - plot.top - plot.bottom;
  const maxDuration = Math.max(...candidates.map(({ candidate }) => candidate.transfer_time_s), 1);
  const maxPropellant = Math.max(...candidates.map(({ propellant }) => propellant.propellant_mass_kg), 1);
  const x = (durationS: number) => plot.left + (durationS / maxDuration) * plotWidth;
  const y = (propellantKg: number) => plot.top + plotHeight - (propellantKg / maxPropellant) * plotHeight;

  return (
    <svg className="pareto-plot" viewBox={`0 0 ${width} ${height}`} role="img" aria-label="Candidate propellant mass versus transfer duration">
      {[0, 0.5, 1].map((fraction) => (
        <g key={fraction}>
          <line className="plot-grid" x1={plot.left} x2={width - plot.right} y1={plot.top + plotHeight * fraction} y2={plot.top + plotHeight * fraction} />
          <text className="plot-tick" x={plot.left - 10} y={plot.top + plotHeight * fraction + 4} textAnchor="end">
            {formatNumber(maxPropellant * (1 - fraction), 0)}
          </text>
          <text className="plot-tick" x={plot.left + plotWidth * fraction} y={height - 23} textAnchor="middle">
            {formatNumber((maxDuration * fraction) / 3600, 1)}
          </text>
        </g>
      ))}
      <text className="plot-axis-label" x={plot.left + plotWidth / 2} y={height - 4} textAnchor="middle">Transfer duration (h)</text>
      <text className="plot-axis-label" transform={`translate(15 ${plot.top + plotHeight / 2}) rotate(-90)`} textAnchor="middle">Propellant (kg)</text>
      {candidates.map(({ candidate, propellant, feasible }) => {
        const isPareto = paretoRouteIds.includes(candidate.route_id);
        const isSelected = selectedRouteId === candidate.route_id;
        return (
          <g
            className={`plot-point ${feasible ? "is-feasible" : "is-infeasible"} ${isPareto ? "is-pareto" : ""} ${isSelected ? "is-selected" : ""}`}
            key={candidate.route_id}
            role="button"
            tabIndex={0}
            aria-label={`${candidate.route_type}, ${formatNumber(propellant.propellant_mass_kg, 1)} kilograms propellant, ${formatNumber(candidate.transfer_time_s / 3600, 2)} hours${isPareto ? ", Pareto optimal" : ""}`}
            onClick={() => onSelect(candidate.route_id)}
            onKeyDown={(event) => {
              if (event.key === "Enter" || event.key === " ") onSelect(candidate.route_id);
            }}
          >
            <circle cx={x(candidate.transfer_time_s)} cy={y(propellant.propellant_mass_kg)} r={isSelected ? 8 : 6} />
            <text className="point-label" x={x(candidate.transfer_time_s) + 10} y={y(propellant.propellant_mass_kg) - 9}>{candidate.route_id}</text>
          </g>
        );
      })}
    </svg>
  );
}

export function App() {
  const [mission, setMission] = useState(initialMission);
  const [analysis, setAnalysis] = useState<MissionAnalysis | null>(null);
  const [selectedRouteId, setSelectedRouteId] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  function updateField(field: "initial_radius_m" | "target_radius_m", value: string) {
    setMission((current) => ({ ...current, [field]: Number(value) }));
  }

  async function submitMission(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setIsLoading(true);
    setError(null);
    try {
      const result = await analyzeMission(mission);
      setAnalysis(result);
      setSelectedRouteId(result.recommendation?.route_id ?? result.candidates[0]?.candidate.route_id ?? "");
    } catch (requestError) {
      setError(requestError instanceof Error ? requestError.message : "Request failed.");
    } finally {
      setIsLoading(false);
    }
  }

  const selectedEvaluation = analysis?.candidates.find(({ candidate }) => candidate.route_id === selectedRouteId);

  return (
    <main className="app-shell">
      <header className="topbar">
        <div className="brand-lockup"><span className="brand-mark">AR</span><div><p className="eyebrow">MISSION CONTROL / 01</p><h1>AstroRoute</h1></div></div>
        <span className="status-chip"><span className="status-dot" /> Backend ready</span>
      </header>
      <section className="intro">
        <div><p className="eyebrow">CIRCULAR ORBIT TRANSFER PLANNER</p><h2>Design the route.<br /><em>Understand the trade-offs.</em></h2><p className="intro-copy">A transparent mission analysis workspace for comparing impulsive Earth-orbit transfers.</p></div>
        <div className="orbit-glyph" aria-hidden="true"><span /><span /><span /></div>
      </section>

      <div className="workspace-grid">
        <form className="panel config-panel" onSubmit={submitMission}>
          <div className="panel-heading"><div><p className="eyebrow">01 / CONFIGURE</p><h3>Mission parameters</h3></div><span className="panel-index">INPUT</span></div>
          <div className="field-grid">
            <label>Initial orbit radius <span>m</span><input type="number" value={mission.initial_radius_m} onChange={(event) => updateField("initial_radius_m", event.target.value)} /></label>
            <label>Target orbit radius <span>m</span><input type="number" value={mission.target_radius_m} onChange={(event) => updateField("target_radius_m", event.target.value)} /></label>
            <label>Spacecraft wet mass <span>kg</span><input type="number" value={mission.constraints.wet_mass_kg} onChange={(event) => setMission((current) => ({ ...current, constraints: { ...current.constraints, wet_mass_kg: Number(event.target.value) } }))} /></label>
            <label>Specific impulse <span>s</span><input type="number" value={mission.constraints.specific_impulse_s} onChange={(event) => setMission((current) => ({ ...current, constraints: { ...current.constraints, specific_impulse_s: Number(event.target.value) } }))} /></label>
          </div>
          <div className="form-divider" />
          <div className="constraint-row"><div><p className="eyebrow">CONSTRAINTS</p><p className="muted">Used by the backend feasibility evaluator.</p></div><div className="constraint-values"><label>Max propellant <span>kg</span><input type="number" value={mission.constraints.max_propellant_mass_kg ?? ""} onChange={(event) => setMission((current) => ({ ...current, constraints: { ...current.constraints, max_propellant_mass_kg: Number(event.target.value) } }))} /></label><label>Max duration <span>s</span><input type="number" value={mission.constraints.max_transfer_time_s ?? ""} onChange={(event) => setMission((current) => ({ ...current, constraints: { ...current.constraints, max_transfer_time_s: Number(event.target.value) } }))} /></label></div></div>
          <button className="primary-button" type="submit" disabled={isLoading}>{isLoading ? "Running analysis…" : "Generate trajectory analysis →"}</button>
          {error && <p className="error-message">{error}</p>}
        </form>

        <section className="panel results-panel">
          <div className="panel-heading"><div><p className="eyebrow">02 / ANALYSIS</p><h3>Route comparison</h3></div><span className="panel-index">LIVE DATA</span></div>
          {!analysis ? <div className="empty-state"><div className="empty-icon">◎</div><p>Configure a mission to run the backend analysis.</p><span>Results will appear here with calculated transfer metrics.</span></div> : <div className="results-content">
            <div className="metric-strip"><div><span>Routes evaluated</span><strong>{analysis.candidates.length}</strong></div><div><span>Pareto routes</span><strong>{analysis.pareto_route_ids.length}</strong></div><div><span>Recommendation</span><strong>{analysis.recommendation?.route_id ?? "—"}</strong></div></div>
            <div className="candidate-list">{analysis.candidates.map((evaluation) => <button className={`candidate ${evaluation.feasible ? "feasible" : "infeasible"} ${selectedRouteId === evaluation.candidate.route_id ? "candidate-selected" : ""}`} key={evaluation.candidate.route_id} onClick={() => setSelectedRouteId(evaluation.candidate.route_id)} type="button"><div><span className="route-status">{evaluation.feasible ? "FEASIBLE" : "REJECTED"}{analysis.pareto_route_ids.includes(evaluation.candidate.route_id) ? " · PARETO" : ""}</span><h4>{evaluation.candidate.route_type}</h4></div><div className="candidate-metric"><span>Δv total</span><strong>{formatNumber(evaluation.candidate.delta_v_total_m_s)} m/s</strong></div><div className="candidate-metric"><span>Propellant</span><strong>{formatNumber(evaluation.propellant.propellant_mass_kg, 1)} kg</strong></div><div className="candidate-metric"><span>Duration</span><strong>{formatNumber(evaluation.candidate.transfer_time_s / 3600, 1)} h</strong></div></button>)}</div>
            {analysis.recommendation && <div className="recommendation"><p className="eyebrow">SYSTEM RECOMMENDATION</p><h4>{analysis.recommendation.route_id}</h4><p>{analysis.recommendation.explanation.join(" ")}</p></div>}
          </div>}
        </section>
      </div>
      {analysis && analysis.candidates.length > 0 && <section className="visualizations-section">
        <p className="eyebrow visualization-section-label">03 / TRAJECTORY & OPTIMIZATION VISUALS</p>
        <div className="visualizations-grid">
          {selectedEvaluation && <section className="visual-panel orbit-panel"><div className="visual-heading"><div><p className="eyebrow">TRAJECTORY / EARTH-CENTERED</p><h4>{selectedEvaluation.candidate.route_type}</h4></div><span className="unit-note">RADIUS · m</span></div><OrbitDiagram candidate={selectedEvaluation.candidate} /><div className="orbit-legend"><span><i className="legend-initial" />Initial orbit</span><span><i className="legend-target" />Target orbit</span><span><i className="legend-transfer" />Transfer arc</span></div></section>}
          <section className="visual-panel pareto-panel"><div className="visual-heading"><div><p className="eyebrow">BACKEND PARETO SET</p><h4>Propellant vs duration</h4></div><span className="unit-note">CLICK A POINT</span></div><ParetoPlot candidates={analysis.candidates} paretoRouteIds={analysis.pareto_route_ids} selectedRouteId={selectedRouteId} onSelect={setSelectedRouteId} /><div className="plot-legend"><span><i className="legend-feasible" />Feasible</span><span><i className="legend-pareto" />Pareto optimal</span><span><i className="legend-infeasible" />Infeasible</span></div></section>
        </div>
      </section>}
    </main>
  );
}
