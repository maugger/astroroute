# AstroRoute

AstroRoute is a transparent spacecraft trajectory-planning prototype. The initial model is intentionally limited to coplanar, impulsive transfers between circular Earth orbits under two-body gravity.

## Current implementation

- SI-unit constants for Earth and standard gravity
- Circular-orbit and vis-viva calculations
- Analytic Hohmann transfer results
- Analytic bi-elliptic transfer results
- Sampled candidate generation and Pareto filtering
- Ideal rocket-equation propellant estimates
- Mission feasibility evaluation for propellant and duration limits
- Reproducible two-body burn-magnitude sensitivity analysis
- End-to-end backend mission analysis and transparent recommendation
- FastAPI health and mission-analysis endpoints
- Pydantic result models
- Input validation and regression tests

The physics engine is independent of any web or visual interface. All displayed metrics must be calculated by this engine rather than hard-coded in a frontend.

## Setup

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e ".[dev]"
pytest
```

## Model limitations

Mission constraints currently support wet mass, specific impulse, maximum propellant mass, and maximum transfer duration. Rejected candidates retain explicit reasons so the decision process remains inspectable.

Sensitivity experiments use a seeded Gaussian burn-magnitude error model and fourth-order Runge-Kutta two-body propagation. They report median, 95th-percentile, and worst terminal radius and speed errors. The sensitivity result is an execution-error metric, not a mission-failure probability.

The backend analysis workflow now generates route candidates, evaluates mission constraints, identifies the delta-v/time Pareto set, runs sensitivity experiments for feasible routes, and produces a deterministic weighted recommendation. Recommendation explanations expose the metrics used; they are decision support, not proof of global optimality.

The optional API exposes the same workflow without duplicating physics logic:

```powershell
python -m uvicorn astroroute.api.app:app --reload
```

Use `GET /health` for a process check and `POST /api/v1/missions/analyze` with a `Mission` payload for analysis. FastAPI also publishes interactive documentation at `/docs`.

Invalid requests return HTTP 422 with a consistent object containing `detail` and an `errors` list. The list contains field-level validation details when request parsing or Pydantic validation fails; physically invalid mission inputs return the explanation in `detail`.

Example request:

```json
{
  "initial_radius_m": 6778137,
  "target_radius_m": 8378137,
  "constraints": {
    "wet_mass_kg": 1000,
    "specific_impulse_s": 320,
    "max_propellant_mass_kg": 1000,
    "max_transfer_time_s": 1000000
  },
  "intermediate_apoapsis_radii_m": [16378137],
  "preferences": {
    "delta_v_weight": 0.5,
    "transfer_time_weight": 0.25,
    "sensitivity_weight": 0.25
  },
  "sensitivity": {
    "samples": 200,
    "burn_magnitude_error_std_fraction": 0.001,
    "random_seed": 42
  }
}
```

The radius values above are request inputs in metres; the response values are calculated by the physics engine. Interactive UI work remains deferred.

The model does not yet include atmospheric drag, J2 perturbations, third-body gravity, finite burns, inclination changes, navigation errors, or mission failure probability. It is a scientific MVP foundation, not flight-certification software.
