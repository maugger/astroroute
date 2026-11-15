import { useState, type FormEvent } from "react";
import { analyzeMission, type MissionAnalysis, type MissionRequest } from "./api";

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

export function App() {
  const [mission, setMission] = useState(initialMission);
  const [analysis, setAnalysis] = useState<MissionAnalysis | null>(null);
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
      setAnalysis(await analyzeMission(mission));
    } catch (requestError) {
      setError(requestError instanceof Error ? requestError.message : "Request failed.");
    } finally {
      setIsLoading(false);
    }
  }

  return (
    <main className="app-shell">
      <header className="topbar">
        <div className="brand-lockup">
          <span className="brand-mark">AR</span>
          <div>
            <p className="eyebrow">MISSION CONTROL / 01</p>
            <h1>AstroRoute</h1>
          </div>
        </div>
        <span className="status-chip"><span className="status-dot" /> Backend ready</span>
      </header>

      <section className="intro">
        <div>
          <p className="eyebrow">CIRCULAR ORBIT TRANSFER PLANNER</p>
          <h2>Design the route.<br /><em>Understand the trade-offs.</em></h2>
          <p className="intro-copy">A transparent mission analysis workspace for comparing impulsive Earth-orbit transfers.</p>
        </div>
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
          {!analysis ? <div className="empty-state"><div className="empty-icon">◎</div><p>Configure a mission to run the backend analysis.</p><span>Results will appear here with calculated transfer metrics.</span></div> : <div className="results-content"><div className="metric-strip"><div><span>Routes evaluated</span><strong>{analysis.candidates.length}</strong></div><div><span>Pareto routes</span><strong>{analysis.pareto_route_ids.length}</strong></div><div><span>Recommendation</span><strong>{analysis.recommendation?.route_id ?? "—"}</strong></div></div><div className="candidate-list">{analysis.candidates.map((evaluation) => <article className={`candidate ${evaluation.feasible ? "feasible" : "infeasible"}`} key={evaluation.candidate.route_id}><div><span className="route-status">{evaluation.feasible ? "FEASIBLE" : "REJECTED"}</span><h4>{evaluation.candidate.route_type}</h4></div><div className="candidate-metric"><span>Δv total</span><strong>{formatNumber(evaluation.candidate.delta_v_total_m_s)} m/s</strong></div><div className="candidate-metric"><span>Propellant</span><strong>{formatNumber(evaluation.propellant.propellant_mass_kg, 1)} kg</strong></div><div className="candidate-metric"><span>Duration</span><strong>{formatNumber(evaluation.candidate.transfer_time_s / 3600, 1)} h</strong></div></article>)}</div>{analysis.recommendation && <div className="recommendation"><p className="eyebrow">SYSTEM RECOMMENDATION</p><h4>{analysis.recommendation.route_id}</h4><p>{analysis.recommendation.explanation.join(" ")}</p></div>}</div>}
        </section>
      </div>
    </main>
  );
}
