"""
Pydantic data validation schemas for BuildPulse.
"""
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, EmailStr, Field


# --- Authentication Models ---
class UserLogin(BaseModel):
    email: str
    password: str


class UserRegister(BaseModel):
    email: str
    password: str = Field(..., min_length=6)
    fullName: str = Field(..., min_length=2)
    role: str = "Project Manager"
    company: Optional[str] = "BuildPulse Construction"


class UserProfile(BaseModel):
    id: str
    email: str
    fullName: str
    role: str
    company: Optional[str] = None


class AuthResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserProfile


# --- Project Models ---
class PhaseProgressUpdate(BaseModel):
    actualProgress: float = Field(..., ge=0.0, le=100.0)


class PhaseModel(BaseModel):
    id: str
    name: str
    weight: float
    plannedStart: str
    plannedEnd: str
    actualStart: Optional[str] = None
    actualEnd: Optional[str] = None
    plannedProgress: float
    actualProgress: float
    status: str
    contractor: str
    criticalPath: bool = False
    delayDays: int = 0


class SupplyChainItem(BaseModel):
    item: str
    supplier: str
    status: str
    delayDays: int
    severity: str


class WeatherForecast(BaseModel):
    upcomingRiskDays: int
    conditions: str
    season: str


class HistoryProgressPoint(BaseModel):
    month: str
    planned: float
    actual: float


class ProjectDetail(BaseModel):
    id: str
    name: str
    code: str
    type: str
    location: str
    contractor: str
    manager: str
    startDate: str
    targetCompletionDate: str
    originalBaselineDate: str
    totalBudget: float
    spentBudget: float
    plannedProgress: float
    actualProgress: float
    weatherImpactDays: int
    workerCount: int
    equipmentCount: int
    safetyIncidentFreeDays: int
    phases: List[PhaseModel]
    supplyChain: List[SupplyChainItem]
    weatherForecast: WeatherForecast
    historyProgress: List[HistoryProgressPoint]


# --- Delay Risk Score Models ---
class RiskFactorBreakdown(BaseModel):
    name: str
    weight: float
    score: float  # 0 to 100
    impact: str   # 'Low', 'Medium', 'High', 'Critical'
    description: str


class RiskRecommendation(BaseModel):
    priority: str
    action: str
    recoveryPotentialDays: int
    estimatedCost: Optional[str] = None


class DelayRiskResult(BaseModel):
    overallRiskScore: int  # 0 to 100
    riskTier: str          # 'Low', 'Moderate', 'High', 'Severe'
    confidence: float
    schedulePerformanceIndex: float  # SPI
    costPerformanceIndex: float      # CPI
    projectedDelayDays: int
    predictedCompletionDate: str
    factors: List[RiskFactorBreakdown]
    recommendations: List[RiskRecommendation]


# --- What-If Analysis Models ---
class WhatIfRequest(BaseModel):
    laborVariancePct: float = Field(0.0, ge=-50.0, le=100.0, description="Labor adjustment % (-50% to +100%)")
    severeWeatherDays: int = Field(0, ge=0, le=30, description="Added severe weather disruption days")
    materialDelayDays: int = Field(0, ge=0, le=60, description="Supply chain/materials delay in days")
    budgetAccelerationAmount: float = Field(0.0, ge=0.0, description="Emergency acceleration budget injection ($)")
    subcontractorEfficiencyPct: float = Field(100.0, ge=40.0, le=160.0, description="Subcontractor speed % (100 is baseline)")


class WhatIfResponse(BaseModel):
    baselineCompletionDate: str
    projectedCompletionDate: str
    netDelayChangeDays: int
    originalRiskScore: int
    simulatedRiskScore: int
    riskChangeDelta: int
    simulatedCostImpact: float
    simulatedSPI: float
    simulatedCPI: float
    summaryAnalysis: str
    impactBreakdown: Dict[str, Any]
    timelineComparison: List[Dict[str, Any]]
