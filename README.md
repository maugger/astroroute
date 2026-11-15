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

The model does not yet include atmospheric drag, J2 perturbations, third-body gravity, finite burns, inclination changes, navigation errors, or mission failure probability. It is a scientific MVP foundation, not flight-certification software.
