# ProcureShield AI — Antigravity Workspace Guidelines

## Project Context
ProcureShield AI is an automated public procurement intelligence and investigation prioritization platform designed to detect collusion, bid-rigging, price anomalies, execution delays, and maintenance cost padding.

## Architecture
- **Backend**: Python 3.11+, FastAPI, SQLAlchemy 2.0, SQLite (`backend/procureshield.db`), Pydantic v2.
  - Virtual Environment: `backend/venv` (interpreter: `backend/venv/bin/python`)
  - Entry point: `backend/app/main.py`
  - Tests: `backend/tests/` (run with `PYTHONPATH=. pytest`)
- **Frontend**: React 18, Vite, TypeScript, Tailwind CSS (`frontend/`)
  - Entry point: `frontend/src/main.tsx`
  - App root: `frontend/src/App.tsx`
  - Build: `npm run build` (outputs to `frontend/dist`)
- **Scripts**: `scripts/generate_dataset.py`, `scripts/seed_database.py`, `scripts/evaluate_benchmark.py`

## Role-Based Access Control (RBAC) Guardrails
- **Only Two Roles**:
  - `INVESTIGATOR`: Access to investigation queue, 360° dossiers, vendor network graphs, and forensic reports.
  - `CITIZEN`: Access to tender search, public audits submission, my submitted audits, and reviewer leaderboard.
- Never add or reintroduce Official, Researcher, or Admin roles.
- Ensure strict backend permission enforcement via `require_investigator` and `require_citizen`.

## Coding & Style Guidelines
- **Single Source of Truth**: All metrics, counts, and signals must come from the database. Never hardcode stats, risk scores, or indicator outputs.
- **Dynamic C1–C20 Indicators**: Always use `AnomalyIndicatorEngine` and database `RiskSignal` records.
- **Responsiveness**: All frontend components must use mobile-first Tailwind breakpoints (`sm:`, `md:`, `lg:`).

## Quick Run Commands
- All-in-one: `./start.sh`
- Backend only: `./run_backend.sh`
- Frontend only: `./run_frontend.sh`
- Test suite: `source backend/venv/bin/activate && PYTHONPATH=. pytest`
