"""
Project Management & Analytics API Endpoints.
"""
from typing import List, Dict, Any
from fastapi import APIRouter, HTTPException, status, Body
from backend.database import db_client
from backend.models import (
    PhaseProgressUpdate,
    DelayRiskResult,
    WhatIfRequest,
    WhatIfResponse
)
from backend.services.risk_engine import calculate_project_risk
from backend.services.simulation import run_what_if_simulation

router = APIRouter(prefix="/api/projects", tags=["Projects"])


@router.get("", response_model=List[Dict[str, Any]])
def list_projects():
    """Retrieves all tracked construction projects."""
    projects = db_client.get_all_projects()
    # Return light summaries
    summaries = []
    for p in projects:
        risk = calculate_project_risk(p)
        summaries.append({
            "id": p["id"],
            "name": p["name"],
            "code": p["code"],
            "type": p["type"],
            "location": p["location"],
            "contractor": p["contractor"],
            "manager": p["manager"],
            "targetCompletionDate": p["targetCompletionDate"],
            "totalBudget": p["totalBudget"],
            "spentBudget": p["spentBudget"],
            "plannedProgress": p["plannedProgress"],
            "actualProgress": p["actualProgress"],
            "riskScore": risk.overallRiskScore,
            "riskTier": risk.riskTier,
            "spi": risk.schedulePerformanceIndex,
            "cpi": risk.costPerformanceIndex,
            "workerCount": p.get("workerCount", 100),
            "safetyDays": p.get("safetyIncidentFreeDays", 100)
        })
    return summaries


@router.get("/{project_id}")
def get_project(project_id: str):
    """Retrieves detailed project timeline, phases, supply chain and progress."""
    project = db_client.get_project_by_id(project_id)
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Project '{project_id}' not found.")
    return project


@router.get("/{project_id}/risk", response_model=DelayRiskResult)
def get_project_delay_risk(project_id: str):
    """Calculates real-time delay risk score and factor decomposition."""
    project = db_client.get_project_by_id(project_id)
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Project '{project_id}' not found.")
    return calculate_project_risk(project)


@router.post("/{project_id}/what-if", response_model=WhatIfResponse)
def run_project_what_if_analysis(project_id: str, scenario: WhatIfRequest):
    """Executes dynamic what-if simulation on schedule, cost, and risk vectors."""
    project = db_client.get_project_by_id(project_id)
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Project '{project_id}' not found.")
    return run_what_if_simulation(project, scenario)


@router.post("/{project_id}/phases/{phase_id}")
def update_phase_progress(project_id: str, phase_id: str, update: PhaseProgressUpdate):
    """Updates actual completion progress for a phase and recalculates project totals."""
    updated_project = db_client.update_project_phase_progress(project_id, phase_id, update.actualProgress)
    if not updated_project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project or phase not found.")
    
    # Recalculate new risk
    risk = calculate_project_risk(updated_project)
    return {
        "message": "Phase progress successfully recorded.",
        "project": updated_project,
        "newOverallProgress": updated_project["actualProgress"],
        "newRiskScore": risk.overallRiskScore,
        "newRiskTier": risk.riskTier
    }


@router.post("/{project_id}/scenarios")
def save_project_scenario(project_id: str, scenario_data: Dict[str, Any] = Body(...)):
    """Saves a simulation what-if contingency plan."""
    project = db_client.get_project_by_id(project_id)
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Project '{project_id}' not found.")
    saved = db_client.save_scenario(project_id, scenario_data)
    return {"message": "Scenario saved successfully.", "scenario": saved}


@router.get("/{project_id}/scenarios")
def get_project_scenarios(project_id: str):
    """Retrieves saved what-if scenario contingency plans for this project."""
    return db_client.get_scenarios(project_id)
