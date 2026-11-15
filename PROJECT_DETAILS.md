# AstroRoute Project Details

## Purpose

AstroRoute is a scientific prototype for comparing spacecraft transfers between circular Earth orbits. It combines a Python analysis backend with a React and TypeScript web interface. The backend is the source of all mission calculations; the frontend presents returned results and supports route comparison.

## Scientific scope

The current model assumes coplanar, impulsive maneuvers and two-body gravity around Earth. It calculates analytic Hohmann and bi-elliptic transfers, then evaluates routes against mission constraints.

The analysis includes:

- Circular-orbit and vis-viva velocity calculations.
- Total maneuver delta-v and transfer duration.
- Ideal rocket-equation propellant estimates.
- Propellant and duration feasibility checks with rejection reasons.
- Delta-v/time Pareto filtering of feasible routes.
- Seeded burn-magnitude sensitivity analysis with median, 95th-percentile, and worst terminal radius and speed errors.
- A deterministic weighted route recommendation with an explanation.

Sensitivity values are execution-error measures. They do not represent mission-failure probabilities.

## Backend

The Python package is under `astroroute/`:

- `astroroute/core/` contains physical calculations, models, validation, candidate evaluation, Pareto filtering, sensitivity analysis, and recommendation logic.
- `astroroute/api/app.py` exposes the backend through FastAPI.
- `tests/` contains the Python regression and API test suite.

Available API routes:

- `GET /health` returns API availability.
- `POST /api/v1/missions/analyze` accepts a validated mission request and returns candidate evaluations, Pareto route IDs, sensitivity results, and a recommendation.
- `/docs` serves FastAPI’s interactive API documentation.

Start the backend from the repository root:

```powershell
python -m uvicorn astroroute.api.app:app --reload
```

## Frontend

The React, TypeScript, and Vite application is in `frontend/`. It includes mission inputs, backend-driven route results, an Earth-centered 2D transfer view, and a propellant-versus-duration plot. The plot marks feasible and infeasible candidates and highlights the Pareto routes. Selecting a route updates the orbit view.

The Vite development server proxies `/api` and `/health` to `http://127.0.0.1:8000`, so run the backend alongside the frontend during local development.

Install dependencies and start the frontend:

```powershell
cd frontend
npm.cmd install
npm.cmd run dev
```

Open the local URL printed by Vite, usually `http://localhost:5173`.

The app uses a dark, black canvas and coss-inspired typography and annotation styling. It uses Inter as the sans-serif face and DM Mono for technical labels.

## Verification commands

From the repository root:

```powershell
pytest
python -m ruff check .
```

From `frontend/`:

```powershell
npm.cmd run lint
npm.cmd run build
```

## Known limitations

The model does not currently include atmospheric drag, J2 perturbations, third-body gravity, finite burns, inclination changes, navigation errors, or mission-failure probability. The frontend currently models Earth and the supported circular-orbit transfer inputs; it does not expose unsupported celestial bodies or physics parameters. The recommendation is transparent decision support, not proof of global optimality or flight certification.
