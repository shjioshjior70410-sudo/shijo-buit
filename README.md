# 🏗️ BuildPulse — Intelligent Construction Project Management Platform

**BuildPulse** is an intelligent, full-stack project management web application engineered for tracking construction site progress, predicting schedule delays, and evaluating risk mitigation strategies in real-time.

Built with a high-performance **FastAPI** backend, **Firebase Firestore** database integration (with seamless zero-config local engine fallback), and a modern, responsive **HTML5/CSS3/JavaScript** frontend with an operations-center dark aesthetic.

---

## 🌟 Key Features

- **🔐 Secure Authentication & Quick Demo Access**:
  - JWT Bearer Token authentication with bcrypt password hashing.
  - Registration and Login flows.
  - **1-Click Demo Evaluation** for *Project Manager* (`Elena Rostova`) and *Site Superintendent* (`Marcus Sterling`).
- **📊 Real-Time Project Overview Metrics**:
  - **Overall Physical Progress**: Planned vs. actual progress percentage with real-time variance calculation.
  - **Budget & Cost Performance**: Total budget, actual spend to date, and Earned Value Management (**CPI** - Cost Performance Index).
  - **Schedule Health**: Target baseline completion vs. projected handover date, schedule slippage in days, and velocity index (**SPI** - Schedule Performance Index).
  - **Site Resources**: Active trade worker headcount, heavy machinery units on site, and consecutive injury-free safety days.
- **📈 Planned vs. Actual S-Curve & Milestone Tracking**:
  - Interactive, responsive SVG **S-Curve Chart** displaying baseline planned vs. actual cumulative progress.
  - Granular breakdown of major construction phases (Substructure, Framing, MEP, Curtain Wall, Interior, Commissioning) with Critical Path flags.
  - **Interactive Progress Update Modal**: Update actual completion percentages directly on the site phases, immediately recalculating project health and risk scores.
- **🎯 Intelligent Multi-Factor Delay Risk Scoring**:
  - Algorithmic composite score from **0 to 100** categorized into *Low*, *Moderate*, *High*, and *Critical* delay risk tiers.
  - Animated SVG semi-circular risk gauge with dynamic color gradients.
  - Detailed decomposition into 5 core risk drivers:
    1. **Schedule Velocity & SPI** (Earned Value schedule variance)
    2. **Critical Path Slippage** (Accumulated bottleneck delays)
    3. **Supply Chain & Material Lead Times** (Delayed rebar, HVAC, steel deliveries)
    4. **Weather & Environmental Hazards** (High wind crane advisories, heavy storm delays)
    5. **Workforce Mobilization Gaps** (Trade headcount shortages)
  - **AI-Driven Schedule Recovery Actions**: Specific recommendations with estimated days recovered and cost projections.
- **🔮 Interactive "What-If" Scenario Simulator**:
  - Dynamic simulation levers with real-time sliders:
    - 👷 **Workforce Capacity Shift** (-40% to +60%)
    - ⛈️ **Severe Weather Disruption** (0 to 14 days)
    - 🚢 **Critical Supply Chain Delays** (0 to 30 days)
    - 💰 **Acceleration Budget Injection** ($0 to $250,000 for emergency overtime / expedited shipping)
    - ⚙️ **Subcontractor Efficiency** (60% to 140%)
  - Instant calculation of **Projected Handover Date**, **Net Schedule Shift**, **Revised Risk Score**, **Financial Cost Impact**, and an automated executive narrative.
  - Save scenarios to the project contingency repository.

---

## 🏛️ Architecture Overview

```
peni website/
├── backend/
│   ├── main.py              # FastAPI application, CORS, static routes, and routers
│   ├── config.py            # Environment configuration & JWT settings
│   ├── database.py          # Firebase Firestore adapter + local persistent engine
│   ├── auth.py              # Password hashing & JWT token validation
│   ├── models.py            # Pydantic data schemas & validation
│   ├── services/
│   │   ├── risk_engine.py   # Multi-factor delay risk scoring algorithm
│   │   └── simulation.py    # What-if schedule elasticity & cost simulation
│   └── routers/
│       ├── auth_routes.py   # /api/auth endpoints (login, register, demo, me)
│       └── project_routes.py# /api/projects, /risk, /what-if, /phases endpoints
├── frontend/
│   ├── index.html           # Main construction intelligence dashboard
│   ├── login.html           # Authentication & quick demo access page
│   ├── css/
│   │   ├── style.css        # Core design system tokens & dark theme
│   │   └── dashboard.css    # Grid layouts, KPI cards, charts, risk gauge
│   └── js/
│       ├── api.js           # Fetch client with token headers & toast alerts
│       ├── auth.js          # Authentication controller
│       ├── risk-gauge.js    # Animated SVG semi-circular gauge & factor renderer
│       ├── what-if.js       # What-if simulation slider controller & results
│       └── dashboard.js     # Dashboard state, S-curve chart, phase updates
├── serviceAccountKey.example.json # Firebase credentials format template
├── requirements.txt         # Python dependencies
├── run.py                   # One-command server launcher
└── README.md                # Detailed documentation
```

---

## 🚀 Quickstart Guide

### 1. Prerequisites
- Python 3.10 or higher installed.

### 2. Install Dependencies
In your terminal, navigate to the project folder and run:
```bash
pip install -r requirements.txt
```

### 3. Launch the Application
Run the startup script:
```bash
python run.py
```
Or directly with uvicorn:
```bash
uvicorn backend.main:app --reload --port 8000
```

### 4. Open in Your Browser
- **Main Dashboard**: [http://localhost:8000/](http://localhost:8000/)
- **Login / Sign Up**: [http://localhost:8000/login](http://localhost:8000/login)
- **Interactive API Documentation (Swagger)**: [http://localhost:8000/docs](http://localhost:8000/docs)

---

## ⚡ Zero-Config vs. Firebase Firestore Setup

BuildPulse is designed with a **hybrid database adapter**:
- **Out of the box**: If no `serviceAccountKey.json` is found, BuildPulse automatically boots up using its **Built-In Local Firestore Engine**, pre-seeded with 3 realistic construction projects (*Skyline Tower Phase 2*, *Harbor View Suspension Bridge*, and *Apex Cloud Data Center*). You can test all features immediately without any external configuration!
- **Production Mode (Firebase Firestore Live)**: When you connect your Firebase credentials, it automatically routes all reads, updates, and persistence directly to Google Cloud Firestore.

### Connecting Your Firebase Firestore Database:
1. Navigate to the [Firebase Console](https://console.firebase.google.com/) and create a new project.
2. In the sidebar, go to **Build** → **Firestore Database** and click **Create Database** (Start in Test Mode or Production Mode).
3. Click the gear icon ⚙️ next to **Project Overview** → **Project Settings**.
4. Go to the **Service accounts** tab.
5. Click **Generate new private key** and confirm.
6. A JSON file will download. Rename it to `serviceAccountKey.json` and place it in the root folder of this project (`peni website/serviceAccountKey.json`).
7. Restart the backend server (`python run.py`).
8. The dashboard status badge in the top navbar will display: **`☁️ Firebase Firestore Live`**.

---

## 👥 Demo User Accounts

You can log in instantly using the 1-click evaluation buttons on the login screen, or with these credentials:

| Role | Email | Password | Assigned Project |
| :--- | :--- | :--- | :--- |
| **Project Manager** | `manager@buildpulse.io` | `manager123` | Skyline Tower Phase 2 |
| **Site Superintendent** | `engineer@buildpulse.io` | `manager123` | Harbor View Suspension Bridge |

*New users can also register an account at `/login` with any email and password.*

---

## 🧮 Mathematical & Analytical Foundations

### 1. Earned Value Schedule Performance (SPI) & Cost Performance (CPI)
$$\text{SPI} = \frac{\text{Actual Progress (\%) } \times \text{Total Budget}}{\text{Planned Progress (\%) } \times \text{Total Budget}} = \frac{\text{Actual Progress}}{\text{Planned Progress}}$$
$$\text{CPI} = \frac{\text{Earned Value}}{\text{Actual Cost}} = \frac{\text{Total Budget} \times (\text{Actual Progress} / 100)}{\text{Spent Budget}}$$

### 2. Multi-Factor Delay Risk Score Formula
$$\text{Risk Score} = 0.35 \times F_{\text{SPI}} + 0.25 \times F_{\text{CriticalPath}} + 0.20 \times F_{\text{SupplyChain}} + 0.10 \times F_{\text{Weather}} + 0.10 \times F_{\text{Labor}}$$
Where:
- $F_{\text{SPI}}$ evaluates the rate of progress deceleration.
- $F_{\text{CriticalPath}}$ weights active critical path tasks with accumulated slippage.
- $F_{\text{SupplyChain}}$ assesses delayed and critical procurement packages.
- $F_{\text{Weather}}$ factors forecast risk days (wind/rain impact on exterior & crane lifts).
- $F_{\text{Labor}}$ calculates trade staffing variance against baseline requirements.

### 3. What-If Schedule Elasticity Model
$$\Delta \text{Delay} = \text{RemainingDays} \times \left(\frac{1}{\text{EffectiveVelocity}} - 1\right) + 1.25 \times \text{WeatherDays} + 0.85 \times \text{MaterialDelay} - \min\left(35, \frac{\text{BudgetInjection}}{\$12,000}\right)$$
$$\text{EffectiveVelocity} = (1 + 0.7 \times \text{LaborVariance}) \times (\text{SubcontractorEfficiency})$$

---

## 📡 REST API Reference

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `POST` | `/api/auth/register` | Register a new user account |
| `POST` | `/api/auth/login` | Authenticate user and receive JWT bearer token |
| `POST` | `/api/auth/demo-login/{role}` | Instant 1-click authentication for demo accounts |
| `GET` | `/api/auth/me` | Fetch authenticated user profile |
| `GET` | `/api/status` | Check Firebase connectivity and database mode |
| `GET` | `/api/projects` | List all construction projects with high-level summaries |
| `GET` | `/api/projects/{id}` | Get full details, phases, and history for a project |
| `GET` | `/api/projects/{id}/risk` | Compute multi-factor delay risk score and AI recommendations |
| `POST` | `/api/projects/{id}/what-if` | Execute dynamic scenario simulation |
| `POST` | `/api/projects/{id}/phases/{phase_id}` | Record site actual progress and recalibrate metrics |
| `POST` | `/api/projects/{id}/scenarios` | Save a simulated contingency scenario |
| `GET` | `/api/projects/{id}/scenarios` | List saved scenarios for a project |

---

## 🧪 Testing & Verification

1. Start the server:
   ```bash
   python run.py
   ```
2. Navigate to `http://localhost:8000/login` and click **⚡ Elena Rostova (Project Manager)**.
3. Observe the dashboard overview metrics, S-Curve chart, and the radial Delay Risk Gauge.
4. Try updating the progress of a phase:
   - Click **Update %** on *Superstructure Steel Framing*.
   - Adjust the progress slider and click **Save Progress & Recalibrate**.
   - Notice how the overall progress and delay risk score update immediately.
5. In the **What-If Analysis Simulator**:
   - Drag **Workforce Capacity Shift** to `+30%` (adding shifts).
   - Drag **Severe Weather Days** to `+4 Days`.
   - Click **⚡ Run What-If Simulation**.
   - Review the revised projected handover date, cost variance, and updated risk score.
#   s h i j o - b u i t  
 #   s h i j o - b u i t  
 #   s h i j o - b u i t  
 #   s h i j o - b u i t  
 #   s h i j o - b u i t  
 