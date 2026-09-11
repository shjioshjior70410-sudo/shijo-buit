"""
Database abstraction layer for BuildPulse.
Supports:
1. Google Cloud Firebase Firestore via firebase-admin SDK
2. High-fidelity local persistent fallback engine for zero-config out-of-the-box operation
"""
import os
import json
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List, Optional
from backend.config import FIREBASE_CREDENTIALS_PATH, BASE_DIR

logger = logging.getLogger("buildpulse.database")
logging.basicConfig(level=logging.INFO)

LOCAL_DB_FILE = BASE_DIR / "local_firestore_data.json"

# Seed Data with rich realistic construction projects
DEFAULT_PROJECTS = [
    {
        "id": "proj-skyline-48",
        "name": "Skyline Tower Phase 2",
        "code": "SKY-T2-2026",
        "type": "Commercial High-Rise",
        "location": "Metropolis Financial District, Lot 4B",
        "contractor": "Apex Structural Builders Corp.",
        "manager": "Elena Rostova, PMP",
        "startDate": "2025-03-01",
        "targetCompletionDate": "2026-11-30",
        "originalBaselineDate": "2026-10-15",
        "totalBudget": 142500000,
        "spentBudget": 86200000,
        "plannedProgress": 64.0,
        "actualProgress": 58.2,
        "weatherImpactDays": 5,
        "workerCount": 184,
        "equipmentCount": 24,
        "safetyIncidentFreeDays": 218,
        "phases": [
            {
                "id": "phase-1",
                "name": "Substructure & Deep Piles",
                "weight": 15,
                "plannedStart": "2025-03-01",
                "plannedEnd": "2025-06-30",
                "actualStart": "2025-03-01",
                "actualEnd": "2025-07-10",
                "plannedProgress": 100,
                "actualProgress": 100,
                "status": "completed",
                "contractor": "Titan Geotech Group",
                "criticalPath": True,
                "delayDays": 10
            },
            {
                "id": "phase-2",
                "name": "Core Concrete & Foundation Raft",
                "weight": 20,
                "plannedStart": "2025-07-01",
                "plannedEnd": "2025-10-31",
                "actualStart": "2025-07-11",
                "actualEnd": "2025-11-15",
                "plannedProgress": 100,
                "actualProgress": 100,
                "status": "completed",
                "contractor": "Apex Structural",
                "criticalPath": True,
                "delayDays": 15
            },
            {
                "id": "phase-3",
                "name": "Superstructure Steel Framing (L1–L32)",
                "weight": 25,
                "plannedStart": "2025-11-01",
                "plannedEnd": "2026-04-15",
                "actualStart": "2025-11-16",
                "actualEnd": None,
                "plannedProgress": 88,
                "actualProgress": 76,
                "status": "delayed",
                "contractor": "Metropolis Ironworks",
                "criticalPath": True,
                "delayDays": 18
            },
            {
                "id": "phase-4",
                "name": "Curtain Wall & Facade Glazing",
                "weight": 15,
                "plannedStart": "2026-02-15",
                "plannedEnd": "2026-07-30",
                "actualStart": "2026-03-01",
                "actualEnd": None,
                "plannedProgress": 42,
                "actualProgress": 34,
                "status": "in_progress",
                "contractor": "AeroGlass Enclosures",
                "criticalPath": False,
                "delayDays": 12
            },
            {
                "id": "phase-5",
                "name": "MEP Rough-Ins (Mechanical, Electrical, Fire)",
                "weight": 15,
                "plannedStart": "2026-03-15",
                "plannedEnd": "2026-09-15",
                "actualStart": "2026-04-01",
                "actualEnd": None,
                "plannedProgress": 32,
                "actualProgress": 22,
                "status": "in_progress",
                "contractor": "Vanguard MEP Solutions",
                "criticalPath": True,
                "delayDays": 14
            },
            {
                "id": "phase-6",
                "name": "Interior Fitouts & Elevator Shafts",
                "weight": 7,
                "plannedStart": "2026-06-01",
                "plannedEnd": "2026-10-31",
                "actualStart": None,
                "actualEnd": None,
                "plannedProgress": 0,
                "actualProgress": 0,
                "status": "pending",
                "contractor": "Luxe Finishes Ltd.",
                "criticalPath": False,
                "delayDays": 0
            },
            {
                "id": "phase-7",
                "name": "Testing, Commissioning & Occupancy Certificate",
                "weight": 3,
                "plannedStart": "2026-10-01",
                "plannedEnd": "2026-11-30",
                "actualStart": None,
                "actualEnd": None,
                "plannedProgress": 0,
                "actualProgress": 0,
                "status": "pending",
                "contractor": "Metropolis City Inspections",
                "criticalPath": True,
                "delayDays": 0
            }
        ],
        "supplyChain": [
            {"item": "High-Tensile Grade 60 Rebar", "supplier": "ArcelorSteel", "status": "delayed", "delayDays": 12, "severity": "high"},
            {"item": "Low-E Double Glazed Curtain Panels", "supplier": "AeroGlass", "status": "on_track", "delayDays": 0, "severity": "low"},
            {"item": "Variable Refrigerant Flow (VRF) Chillers", "supplier": "Carrier Industrial", "status": "risk", "delayDays": 8, "severity": "medium"}
        ],
        "weatherForecast": {
            "upcomingRiskDays": 4,
            "conditions": "High wind warnings (>45 mph) impacting crane operations on levels 24+",
            "season": "Spring Storm Transition"
        },
        "historyProgress": [
            {"month": "Mar '25", "planned": 4.0, "actual": 4.0},
            {"month": "May '25", "planned": 12.5, "actual": 11.2},
            {"month": "Jul '25", "planned": 23.0, "actual": 20.5},
            {"month": "Sep '25", "planned": 36.0, "actual": 33.0},
            {"month": "Nov '25", "planned": 47.0, "actual": 43.5},
            {"month": "Jan '26", "planned": 55.0, "actual": 50.0},
            {"month": "Mar '26", "planned": 64.0, "actual": 58.2}
        ]
    },
    {
        "id": "proj-harbor-bridge",
        "name": "Harbor View Suspension Bridge",
        "code": "HVB-2024-X",
        "type": "Civil Infrastructure",
        "location": "Coastal Bay Corridor, Pier 12 to North Pier",
        "contractor": "Pacific Marine Infrastructure",
        "manager": "Marcus Sterling, PE",
        "startDate": "2024-06-01",
        "targetCompletionDate": "2027-04-30",
        "originalBaselineDate": "2027-04-30",
        "totalBudget": 320000000,
        "spentBudget": 128500000,
        "plannedProgress": 42.0,
        "actualProgress": 41.3,
        "weatherImpactDays": 8,
        "workerCount": 260,
        "equipmentCount": 42,
        "safetyIncidentFreeDays": 412,
        "phases": [
            {
                "id": "h-phase-1",
                "name": "Deep Water Caissons & Pier 1 Foundation",
                "weight": 25,
                "plannedStart": "2024-06-01",
                "plannedEnd": "2025-02-28",
                "actualStart": "2024-06-01",
                "actualEnd": "2025-03-05",
                "plannedProgress": 100,
                "actualProgress": 100,
                "status": "completed",
                "contractor": "DeepOcean Civil",
                "criticalPath": True,
                "delayDays": 5
            },
            {
                "id": "h-phase-2",
                "name": "Main Suspension Towers (North & South)",
                "weight": 30,
                "plannedStart": "2025-03-01",
                "plannedEnd": "2026-05-30",
                "actualStart": "2025-03-10",
                "actualEnd": None,
                "plannedProgress": 78,
                "actualProgress": 76,
                "status": "in_progress",
                "contractor": "Pacific Marine",
                "criticalPath": True,
                "delayDays": 4
            },
            {
                "id": "h-phase-3",
                "name": "Main Cable Spinning & Anchorage Tying",
                "weight": 25,
                "plannedStart": "2026-06-01",
                "plannedEnd": "2026-11-30",
                "actualStart": None,
                "actualEnd": None,
                "plannedProgress": 0,
                "actualProgress": 0,
                "status": "pending",
                "contractor": "WireTech Global",
                "criticalPath": True,
                "delayDays": 0
            },
            {
                "id": "h-phase-4",
                "name": "Deck Truss Assembly & Roadway Surfacing",
                "weight": 20,
                "plannedStart": "2026-12-01",
                "plannedEnd": "2027-04-30",
                "actualStart": None,
                "actualEnd": None,
                "plannedProgress": 0,
                "actualProgress": 0,
                "status": "pending",
                "contractor": "Pacific Marine",
                "criticalPath": True,
                "delayDays": 0
            }
        ],
        "supplyChain": [
            {"item": "Galvanized Cable Wire Coils", "supplier": "Nippon Steel Corp", "status": "on_track", "delayDays": 0, "severity": "low"},
            {"item": "Orthotropic Steel Deck Sections", "supplier": "Hyundai Heavy", "status": "on_track", "delayDays": 0, "severity": "low"}
        ],
        "weatherForecast": {
            "upcomingRiskDays": 2,
            "conditions": "Mild marine fog, normal tide levels within operational envelope",
            "season": "Coastal Spring"
        },
        "historyProgress": [
            {"month": "Jun '24", "planned": 5.0, "actual": 4.8},
            {"month": "Oct '24", "planned": 14.0, "actual": 13.5},
            {"month": "Feb '25", "planned": 24.5, "actual": 24.0},
            {"month": "Jun '25", "planned": 32.0, "actual": 31.2},
            {"month": "Oct '25", "planned": 38.0, "actual": 37.5},
            {"month": "Mar '26", "planned": 42.0, "actual": 41.3}
        ]
    },
    {
        "id": "proj-apex-datacenter",
        "name": "Apex Cloud Data Center Hyperscale",
        "code": "APX-DC-HYP4",
        "type": "Mission-Critical Tech Facility",
        "location": "Northwest Industrial Technology Corridor",
        "contractor": "HyperScale Engineering Group",
        "manager": "Samantha Wu, Lead Superintendent",
        "startDate": "2025-06-01",
        "targetCompletionDate": "2026-08-31",
        "originalBaselineDate": "2026-06-15",
        "totalBudget": 88000000,
        "spentBudget": 69400000,
        "plannedProgress": 82.0,
        "actualProgress": 70.8,
        "weatherImpactDays": 2,
        "workerCount": 112,
        "equipmentCount": 16,
        "safetyIncidentFreeDays": 284,
        "phases": [
            {
                "id": "dc-phase-1",
                "name": "Civil Earthworks & Security Perimeter",
                "weight": 15,
                "plannedStart": "2025-06-01",
                "plannedEnd": "2025-08-31",
                "actualStart": "2025-06-01",
                "actualEnd": "2025-09-05",
                "plannedProgress": 100,
                "actualProgress": 100,
                "status": "completed",
                "contractor": "Precision Grading",
                "criticalPath": False,
                "delayDays": 5
            },
            {
                "id": "dc-phase-2",
                "name": "Precast Concrete Enclosure & Storm Shell",
                "weight": 25,
                "plannedStart": "2025-09-01",
                "plannedEnd": "2025-12-15",
                "actualStart": "2025-09-06",
                "actualEnd": "2025-12-28",
                "plannedProgress": 100,
                "actualProgress": 100,
                "status": "completed",
                "contractor": "Precast Dynamics",
                "criticalPath": True,
                "delayDays": 13
            },
            {
                "id": "dc-phase-3",
                "name": "MV Substation & Medium Voltage Switchgear",
                "weight": 25,
                "plannedStart": "2025-12-15",
                "plannedEnd": "2026-03-31",
                "actualStart": "2026-01-05",
                "actualEnd": None,
                "plannedProgress": 95,
                "actualProgress": 78,
                "status": "delayed",
                "contractor": "ElectroPower Systems",
                "criticalPath": True,
                "delayDays": 28
            },
            {
                "id": "dc-phase-4",
                "name": "Liquid Cooling Distribution & CRAC Chiller Units",
                "weight": 25,
                "plannedStart": "2026-02-01",
                "plannedEnd": "2026-06-15",
                "actualStart": "2026-02-20",
                "actualEnd": None,
                "plannedProgress": 52,
                "actualProgress": 32,
                "status": "delayed",
                "contractor": "ArcticCool Thermal",
                "criticalPath": True,
                "delayDays": 30
            },
            {
                "id": "dc-phase-5",
                "name": "Integrated Systems Commissioning (IST Level 5)",
                "weight": 10,
                "plannedStart": "2026-06-16",
                "plannedEnd": "2026-08-31",
                "actualStart": None,
                "actualEnd": None,
                "plannedProgress": 0,
                "actualProgress": 0,
                "status": "pending",
                "contractor": "Commissioning Agents Inc.",
                "criticalPath": True,
                "delayDays": 0
            }
        ],
        "supplyChain": [
            {"item": "34.5kV Vacuum Circuit Breakers", "supplier": "Siemens Energy", "status": "critical_delay", "delayDays": 28, "severity": "high"},
            {"item": "Closed-Loop Cooling Towers", "supplier": "EVAPCO", "status": "delayed", "delayDays": 22, "severity": "high"},
            {"item": "2.5MW Emergency Diesel Generators", "supplier": "Cummins Power", "status": "on_track", "delayDays": 0, "severity": "low"}
        ],
        "weatherForecast": {
            "upcomingRiskDays": 1,
            "conditions": "Normal interior conditioning, minimal climate exposure",
            "season": "Spring Mild"
        },
        "historyProgress": [
            {"month": "Jun '25", "planned": 8.0, "actual": 7.5},
            {"month": "Aug '25", "planned": 22.0, "actual": 20.0},
            {"month": "Oct '25", "planned": 40.0, "actual": 36.5},
            {"month": "Dec '25", "planned": 58.0, "actual": 52.0},
            {"month": "Jan '26", "planned": 70.0, "actual": 62.0},
            {"month": "Mar '26", "planned": 82.0, "actual": 70.8}
        ]
    }
]

# Default demo users (passwords hashed via bcrypt: 'admin123' and 'engineer123')
# We store both raw for fallback demo checks and hashed for standard auth
DEFAULT_USERS = [
    {
        "id": "user-1",
        "email": "manager@buildpulse.io",
        "fullName": "Elena Rostova",
        "role": "Project Manager",
        "passwordHash": "$2b$12$eZ/52nZ4L7xZ7K8Bq3G.Nuq7u09X4s8oFfF6O4y3n9v2z8R1x5Bfa", # manager123
        "company": "Apex Structural Builders Corp."
    },
    {
        "id": "user-2",
        "email": "engineer@buildpulse.io",
        "fullName": "Marcus Sterling",
        "role": "Site Superintendent",
        "passwordHash": "$2b$12$eZ/52nZ4L7xZ7K8Bq3G.Nuq7u09X4s8oFfF6O4y3n9v2z8R1x5Bfa", # manager123
        "company": "Pacific Marine Infrastructure"
    }
]


class DatabaseManager:
    def __init__(self):
        self.is_firebase_live = False
        self.db = None
        self.local_cache = {
            "projects": {p["id"]: p for p in DEFAULT_PROJECTS},
            "users": {u["email"].lower(): u for u in DEFAULT_USERS},
            "scenarios": {}
        }
        self._init_database()

    def _init_database(self):
        """Initializes Firebase Firestore if valid credentials exist, else loads local JSON cache."""
        creds_path = Path(FIREBASE_CREDENTIALS_PATH)
        if creds_path.exists():
            try:
                import firebase_admin
                from firebase_admin import credentials, firestore
                
                # Check if already initialized
                if not firebase_admin._apps:
                    cred = credentials.Certificate(str(creds_path))
                    firebase_admin.initialize_app(cred)
                self.db = firestore.client()
                self.is_firebase_live = True
                logger.info("Connected to Firebase Firestore successfully.")
                self._seed_firebase_if_empty()
                return
            except Exception as e:
                logger.warning(f"Failed to initialize Firebase Admin SDK: {e}. Falling back to Local Firestore Engine.")
        else:
            logger.info(f"No Firebase credentials found at '{creds_path}'. Using Built-in Local Firestore Engine.")

        # Local fallback persistence initialization
        self._load_local_data()

    def _load_local_data(self):
        """Loads data from local JSON file or saves defaults."""
        if LOCAL_DB_FILE.exists():
            try:
                with open(LOCAL_DB_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.local_cache["projects"] = data.get("projects", self.local_cache["projects"])
                    self.local_cache["users"] = data.get("users", self.local_cache["users"])
                    self.local_cache["scenarios"] = data.get("scenarios", {})
                    logger.info("Loaded project and user data from local persistent cache.")
                    return
            except Exception as e:
                logger.error(f"Error loading local JSON cache: {e}. Using default seeds.")

        self._save_local_data()

    def _save_local_data(self):
        """Persists local database cache to disk."""
        try:
            with open(LOCAL_DB_FILE, "w", encoding="utf-8") as f:
                json.dump(self.local_cache, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save local database cache: {e}")

    def _seed_firebase_if_empty(self):
        """Seeds initial construction projects and demo users into Firebase Firestore if empty."""
        try:
            proj_ref = self.db.collection("projects").limit(1).get()
            if len(list(proj_ref)) == 0:
                logger.info("Seeding Firebase Firestore with initial projects...")
                batch = self.db.batch()
                for p in DEFAULT_PROJECTS:
                    doc_ref = self.db.collection("projects").document(p["id"])
                    batch.set(doc_ref, p)
                for u in DEFAULT_USERS:
                    user_ref = self.db.collection("users").document(u["email"].lower())
                    batch.set(user_ref, u)
                batch.commit()
                logger.info("Firebase Firestore seeding complete.")
        except Exception as e:
            logger.error(f"Failed to seed Firebase Firestore: {e}")

    # --- Project Methods ---
    def get_all_projects(self) -> List[Dict[str, Any]]:
        if self.is_firebase_live:
            try:
                docs = self.db.collection("projects").stream()
                projects = [doc.to_dict() for doc in docs]
                return projects or list(self.local_cache["projects"].values())
            except Exception as e:
                logger.error(f"Firestore get_all_projects failed: {e}")
        return list(self.local_cache["projects"].values())

    def get_project_by_id(self, project_id: str) -> Optional[Dict[str, Any]]:
        if self.is_firebase_live:
            try:
                doc = self.db.collection("projects").document(project_id).get()
                if doc.exists:
                    return doc.to_dict()
            except Exception as e:
                logger.error(f"Firestore get_project_by_id failed: {e}")
        return self.local_cache["projects"].get(project_id)

    def update_project_phase_progress(self, project_id: str, phase_id: str, new_progress: float) -> Optional[Dict[str, Any]]:
        project = self.get_project_by_id(project_id)
        if not project:
            return None

        phases = project.get("phases", [])
        updated = False
        total_actual = 0.0

        for ph in phases:
            if ph["id"] == phase_id:
                ph["actualProgress"] = max(0.0, min(100.0, float(new_progress)))
                if ph["actualProgress"] == 100:
                    ph["status"] = "completed"
                elif ph["actualProgress"] > 0:
                    ph["status"] = "in_progress"
                updated = True
            # Compute weighted actual progress
            weight = ph.get("weight", 100 / len(phases))
            total_actual += (ph.get("actualProgress", 0.0) * (weight / 100.0))

        if updated:
            project["actualProgress"] = round(total_actual, 1)
            project["phases"] = phases

            # Save in Firebase if live
            if self.is_firebase_live:
                try:
                    self.db.collection("projects").document(project_id).set(project)
                except Exception as e:
                    logger.error(f"Firestore update failed: {e}")

            # Also update local cache
            self.local_cache["projects"][project_id] = project
            self._save_local_data()
            return project
        return None

    # --- Scenario Methods ---
    def save_scenario(self, project_id: str, scenario: Dict[str, Any]) -> Dict[str, Any]:
        scenario["createdAt"] = datetime.utcnow().isoformat()
        if self.is_firebase_live:
            try:
                doc_ref = self.db.collection("projects").document(project_id).collection("scenarios").document()
                scenario["id"] = doc_ref.id
                doc_ref.set(scenario)
                return scenario
            except Exception as e:
                logger.error(f"Firestore save_scenario failed: {e}")

        # Local cache
        if project_id not in self.local_cache["scenarios"]:
            self.local_cache["scenarios"][project_id] = []
        scenario["id"] = f"scen-{len(self.local_cache['scenarios'][project_id]) + 1}"
        self.local_cache["scenarios"][project_id].append(scenario)
        self._save_local_data()
        return scenario

    def get_scenarios(self, project_id: str) -> List[Dict[str, Any]]:
        if self.is_firebase_live:
            try:
                docs = self.db.collection("projects").document(project_id).collection("scenarios").stream()
                scens = [d.to_dict() for d in docs]
                if scens:
                    return scens
            except Exception as e:
                logger.error(f"Firestore get_scenarios failed: {e}")
        return self.local_cache["scenarios"].get(project_id, [])

    # --- User / Auth Methods ---
    def get_user_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        email_key = email.strip().lower()
        if self.is_firebase_live:
            try:
                doc = self.db.collection("users").document(email_key).get()
                if doc.exists:
                    return doc.to_dict()
            except Exception as e:
                logger.error(f"Firestore get_user_by_email failed: {e}")
        return self.local_cache["users"].get(email_key)

    def create_user(self, user_dict: Dict[str, Any]) -> Dict[str, Any]:
        email_key = user_dict["email"].strip().lower()
        if self.is_firebase_live:
            try:
                self.db.collection("users").document(email_key).set(user_dict)
            except Exception as e:
                logger.error(f"Firestore create_user failed: {e}")

        self.local_cache["users"][email_key] = user_dict
        self._save_local_data()
        return user_dict

    def get_status(self) -> Dict[str, Any]:
        return {
            "mode": "Firebase Cloud Firestore" if self.is_firebase_live else "Local Firestore Engine",
            "isFirebaseLive": self.is_firebase_live,
            "projectCount": len(self.local_cache["projects"]),
            "timestamp": datetime.utcnow().isoformat()
        }


# Singleton database instance
db_client = DatabaseManager()
