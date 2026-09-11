"""
What-If Scenario Simulation Engine.
Analyzes project schedule elasticity under variable labor, weather, supply chain,
and budget acceleration conditions.
"""
from datetime import datetime, timedelta
from typing import Dict, Any, List
from backend.models import WhatIfRequest, WhatIfResponse
from backend.services.risk_engine import calculate_project_risk


def run_what_if_simulation(project: Dict[str, Any], scenario: WhatIfRequest) -> WhatIfResponse:
    """Simulates impacts of dynamic schedule adjustments and risk variables."""
    # 1. Baseline analysis
    base_risk = calculate_project_risk(project)
    original_score = base_risk.overallRiskScore
    original_delay = base_risk.projectedDelayDays

    target_date_str = project.get("targetCompletionDate", "2026-11-30")
    try:
        target_dt = datetime.strptime(target_date_str, "%Y-%m-%d")
    except Exception:
        target_dt = datetime.utcnow() + timedelta(days=180)

    # Base predicted date
    baseline_completion_dt = target_dt + timedelta(days=original_delay)
    baseline_completion_str = baseline_completion_dt.strftime("%Y-%m-%d")

    # 2. Variable modeling
    # Remaining project calendar days estimate
    remaining_days_est = max(30, (target_dt - datetime.utcnow()).days) if (target_dt > datetime.utcnow()) else 120

    # Labor elasticity: workforce headcount variation impacts velocity
    # e.g., +20% labor yields ~14% velocity increase (diminishing marginal returns in construction)
    labor_factor = 1.0 + (scenario.laborVariancePct / 100.0) * 0.70
    labor_factor = max(0.4, min(1.8, labor_factor))

    # Subcontractor productivity factor
    sub_factor = scenario.subcontractorEfficiencyPct / 100.0

    # Combined velocity factor
    effective_velocity = labor_factor * sub_factor

    # Velocity schedule effect in days
    # If effective_velocity = 0.8, remaining work takes 1.25x -> +25% days
    velocity_delta_days = round(remaining_days_est * ((1.0 / effective_velocity) - 1.0))

    # Weather impact: 1 day of severe weather causes 1.25 days lost due to site drying/safety stops
    weather_loss_days = round(scenario.severeWeatherDays * 1.25)

    # Material/Supply delay: critical path absorption buffer ~20%
    material_loss_days = round(scenario.materialDelayDays * 0.85)

    # Budget acceleration: emergency expedited work recovers ~1 day per $12,000 injected
    accelerated_recovered_days = round(scenario.budgetAccelerationAmount / 12000.0)
    accelerated_recovered_days = min(35, accelerated_recovered_days)

    # Net change in delay (relative to current baseline delay)
    net_delay_change = velocity_delta_days + weather_loss_days + material_loss_days - accelerated_recovered_days
    simulated_total_delay = max(0, original_delay + net_delay_change)

    # New completion date
    simulated_completion_dt = target_dt + timedelta(days=simulated_total_delay)
    simulated_completion_str = simulated_completion_dt.strftime("%Y-%m-%d")

    # 3. Cost impact calculation
    total_budget = float(project.get("totalBudget", 100000000))
    # Daily general contractor site overhead (General Conditions) is roughly 0.008% of project budget / day
    daily_site_overhead = max(2500.0, total_budget * 0.00008)
    extended_overhead_cost = net_delay_change * daily_site_overhead if net_delay_change > 0 else (net_delay_change * daily_site_overhead * 0.5)

    # Additional labor cost variance
    labor_cost_delta = (scenario.laborVariancePct / 100.0) * (total_budget * 0.15) * (remaining_days_est / 365.0)

    total_cost_impact = round(extended_overhead_cost + labor_cost_delta + scenario.budgetAccelerationAmount, 2)

    # 4. Simulated SPI and CPI
    base_spi = base_risk.schedulePerformanceIndex
    simulated_spi = round(max(0.4, min(1.35, base_spi * effective_velocity - (scenario.severeWeatherDays * 0.015) - (scenario.materialDelayDays * 0.012))), 2)

    base_cpi = base_risk.costPerformanceIndex
    cost_increase_ratio = 1.0 + (total_cost_impact / max(1000000.0, total_budget))
    simulated_cpi = round(max(0.5, min(1.3, base_cpi / max(0.8, cost_increase_ratio))), 2)

    # 5. Simulated Risk Score
    # Shifts in risk score based on new SPI and delay
    risk_delta = round((net_delay_change * 0.85) - (scenario.laborVariancePct * 0.25) + (scenario.severeWeatherDays * 2.5) + (scenario.materialDelayDays * 1.8) - (accelerated_recovered_days * 1.5))
    simulated_risk_score = max(5, min(99, original_score + risk_delta))

    # 6. Timeline comparison data points for chart
    timeline_comparison = [
        {"milestone": "Current Position", "planned": float(project.get("plannedProgress", 60)), "baselineActual": float(project.get("actualProgress", 55)), "simulated": float(project.get("actualProgress", 55))},
        {"milestone": "+30 Days", "planned": min(100.0, float(project.get("plannedProgress", 60)) + 12), "baselineActual": min(100.0, float(project.get("actualProgress", 55)) + (12 * base_spi)), "simulated": min(100.0, float(project.get("actualProgress", 55)) + (12 * simulated_spi))},
        {"milestone": "+60 Days", "planned": min(100.0, float(project.get("plannedProgress", 60)) + 24), "baselineActual": min(100.0, float(project.get("actualProgress", 55)) + (24 * base_spi)), "simulated": min(100.0, float(project.get("actualProgress", 55)) + (24 * simulated_spi))},
        {"milestone": "+90 Days", "planned": min(100.0, float(project.get("plannedProgress", 60)) + 36), "baselineActual": min(100.0, float(project.get("actualProgress", 55)) + (36 * base_spi)), "simulated": min(100.0, float(project.get("actualProgress", 55)) + (36 * simulated_spi))},
        {"milestone": "Project Handover", "planned": 100.0, "baselineActual": 100.0, "simulated": 100.0}
    ]

    # 7. Executive Summary narrative
    delay_word = "later" if net_delay_change > 0 else "earlier"
    abs_net_days = abs(net_delay_change)
    summary_parts = []

    if net_delay_change > 0:
        summary_parts.append(f"Under this scenario, completion shifts {abs_net_days} days {delay_word} to {simulated_completion_str}.")
    elif net_delay_change < 0:
        summary_parts.append(f"Under this acceleration scenario, the project recovers {abs_net_days} days, advancing completion to {simulated_completion_str}.")
    else:
        summary_parts.append(f"This scenario neutralizes baseline delays, holding completion steady at {simulated_completion_str}.")

    if total_cost_impact > 0:
        summary_parts.append(f"Estimated financial impact is a budget increase of ${total_cost_impact:,.0f} (extended site overhead and expedite costs).")
    elif total_cost_impact < 0:
        summary_parts.append(f"Estimated savings of ${abs(total_cost_impact):,.0f} through expedited schedule efficiencies.")

    risk_shift_desc = f"Risk score changes by {risk_delta:+d} points (from {original_score} to {simulated_risk_score})."
    summary_parts.append(risk_shift_desc)

    return WhatIfResponse(
        baselineCompletionDate=baseline_completion_str,
        projectedCompletionDate=simulated_completion_str,
        netDelayChangeDays=net_delay_change,
        originalRiskScore=original_score,
        simulatedRiskScore=simulated_risk_score,
        riskChangeDelta=risk_delta,
        simulatedCostImpact=total_cost_impact,
        simulatedSPI=simulated_spi,
        simulatedCPI=simulated_cpi,
        summaryAnalysis=" ".join(summary_parts),
        impactBreakdown={
            "velocityDeltaDays": velocity_delta_days,
            "weatherLossDays": weather_loss_days,
            "materialLossDays": material_loss_days,
            "acceleratedRecoveredDays": accelerated_recovered_days,
            "dailySiteOverhead": daily_site_overhead
        },
        timelineComparison=timeline_comparison
    )
