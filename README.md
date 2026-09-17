# ProcureShield AI — Public Procurement Integrity & Vigilance Monitoring Platform

ProcureShield AI is a full-stack, automated intelligence and vigilance platform designed to detect collusion, bid-rigging, price gouging, project execution delays, quality anomalies, and post-award maintenance padding in public procurement tenders.

---

## 🏛️ Key Features

- **Automated Anomaly Detection Engine (C1–C20)**: Real-time detection across 20 procurement indicators covering pricing deviations, tight bid clustering, repeat co-bidding cartels, directorship nexus, execution delays, and excessive maintenance cost ratios.
- **Single Source of Truth**: Completely driven by SQLite / PostgreSQL database schemas with realistic synthetic public works data (500 Tenders, 50 Vendors, 2,968 Bids, 500 Contracts, 492 Risk Signals, and 40 Citizen Audits).
- **Strict Role-Based Access Control (RBAC)**:
  - **Lead Investigator** (`INVESTIGATOR`): Access to the full Investigation Priority Queue, 360° Case Dossiers, Vendor Nexus Network Graphs, and Forensic Reports.
  - **Citizen Reviewer** (`CITIZEN`): Empaneled public workflow to search tenders, submit verified geo-tagged defect audits with photo evidence, build community reputation scores, and track review verification.
- **360° Case Investigation Dossier**: Complete lifecycle visibility spanning procurement & bids, execution milestones, quality audit inspections, verified citizen reports, and maintenance claims.
- **Multi-Format Export & Sharing**: Export full forensic dossiers as JSON, download summary spreadsheets as CSV, or generate print/PDF audit reports.
- **Fully Responsive Architecture**: Mobile drawer navigation, adaptive tables with card views on smartphones, and multi-column desktop views.

---

## 🚀 Quick Start Guide

### Prerequisites
- Python 3.11+
- Node.js 18+ and npm

---

### 1. Backend Setup (FastAPI + SQLite/PostgreSQL)

```bash
# Navigate to backend directory
cd backend

# Create and activate Python virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# (Optional) Re-seed the database if needed:
# python -m scripts.seed_database

# Start the backend server
uvicorn backend.app.main:app --host 127.0.0.1 --port 8000 --reload
```

The backend will be available at:
- **API Root**: [http://127.0.0.1:8000](http://127.0.0.1:8000)
- **Interactive Swagger Docs**: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- **OpenAPI JSON Schema**: [http://127.0.0.1:8000/openapi.json](http://127.0.0.1:8000/openapi.json)

To run the automated backend test suite:
```bash
PYTHONPATH=. pytest
```

---

### 2. Frontend Setup (React 18 + Vite + TypeScript + Tailwind CSS)

```bash
# Navigate to frontend directory
cd frontend

# Install node dependencies
npm install

# Start development server
npm run dev

# Or build for production
npm run build
```

The frontend will be available at:
- **Web App**: [http://127.0.0.1:5173](http://127.0.0.1:5173)

---

## 👥 Demo Logins

| Persona | Name | Email | Password | Role |
|---|---|---|---|---|
| **Lead Investigator** | Sarah Chen | `sarah.chen@procureshield.gov.in` | `investigator123` | `INVESTIGATOR` |
| **Citizen Reviewer** | Rohan Verma | `rohan.verma@gmail.com` | `citizen123` | `CITIZEN` |

You can also use the one-click demo login buttons directly inside the app login modal.

---

## 📂 Project Directory Structure

```
procureshield/
├── backend/
│   ├── app/
│   │   ├── api/             # FastAPI REST endpoints (auth, alerts, tenders, vendors, complaints, analytics)
│   │   ├── core/            # Database engine, JWT security, RBAC middlewares, settings
│   │   ├── models/          # SQLAlchemy entity models (Tenders, Vendors, Bids, Investigations, Complaints, etc.)
│   │   ├── schemas/         # Pydantic validation & response schemas
│   │   └── services/        # Anomaly detection engine (C1-C20 indicators) & graph builders
│   ├── procureshield.db     # Pre-seeded SQLite database with full dataset
│   ├── requirements.txt     # Python dependency specifications
│   └── tests/               # 39 automated pytest test suites
├── frontend/
│   ├── src/
│   │   ├── components/      # Responsive UI components (Sidebar, TopHeader, NetworkGraph, Modals)
│   │   ├── pages/           # Pages (InvestigatorDashboard, CaseDetail360, CitizenDashboard, Tenders, Vendors, Leaderboard)
│   │   ├── services/        # Typed API client
│   │   └── types/           # TypeScript interface definitions
│   ├── package.json
│   └── vite.config.ts
├── scripts/
│   ├── generate_dataset.py  # Synthetic procurement dataset generator
│   ├── seed_database.py     # Database seeder linking entities & indicators
│   ├── evaluate_benchmark.py# Anomaly detection precision & recall benchmark
│   └── schema_postgres.sql  # Production PostgreSQL DDL
├── data/
│   └── generated/           # Raw generated dataset CSV files
└── requirements.txt         # Root Python requirements
```
