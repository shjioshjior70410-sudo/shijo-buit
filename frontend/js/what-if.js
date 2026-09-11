/**
 * BuildPulse What-If Scenario Analysis Controller
 */

let currentSimulationResult = null;

function initWhatIfSimulator() {
  const laborSlider = document.getElementById('sim-labor');
  const weatherSlider = document.getElementById('sim-weather');
  const materialSlider = document.getElementById('sim-materials');
  const budgetSlider = document.getElementById('sim-budget');
  const efficiencySlider = document.getElementById('sim-efficiency');

  const laborVal = document.getElementById('sim-labor-val');
  const weatherVal = document.getElementById('sim-weather-val');
  const materialVal = document.getElementById('sim-materials-val');
  const budgetVal = document.getElementById('sim-budget-val');
  const efficiencyVal = document.getElementById('sim-efficiency-val');

  // Slider event listeners for live feedback
  if (laborSlider && laborVal) {
    laborSlider.addEventListener('input', (e) => {
      const val = parseInt(e.target.value);
      laborVal.textContent = (val > 0 ? `+${val}%` : `${val}%`);
    });
  }

  if (weatherSlider && weatherVal) {
    weatherSlider.addEventListener('input', (e) => {
      weatherVal.textContent = `+${e.target.value} Days`;
    });
  }

  if (materialSlider && materialVal) {
    materialSlider.addEventListener('input', (e) => {
      materialVal.textContent = `+${e.target.value} Days`;
    });
  }

  if (budgetSlider && budgetVal) {
    budgetSlider.addEventListener('input', (e) => {
      const val = parseInt(e.target.value);
      budgetVal.textContent = `$${val.toLocaleString()}`;
    });
  }

  if (efficiencySlider && efficiencyVal) {
    efficiencySlider.addEventListener('input', (e) => {
      efficiencyVal.textContent = `${e.target.value}%`;
    });
  }

  // Run Simulation Button
  const runBtn = document.getElementById('btn-run-simulation');
  if (runBtn) {
    runBtn.addEventListener('click', triggerSimulation);
  }

  // Reset Button
  const resetBtn = document.getElementById('btn-reset-simulation');
  if (resetBtn) {
    resetBtn.addEventListener('click', () => {
      if (laborSlider) { laborSlider.value = 0; laborVal.textContent = '0%'; }
      if (weatherSlider) { weatherSlider.value = 0; weatherVal.textContent = '+0 Days'; }
      if (materialSlider) { materialSlider.value = 0; materialVal.textContent = '+0 Days'; }
      if (budgetSlider) { budgetSlider.value = 0; budgetVal.textContent = '$0'; }
      if (efficiencySlider) { efficiencySlider.value = 100; efficiencyVal.textContent = '100%'; }
      triggerSimulation();
    });
  }

  // Save Scenario Button
  const saveBtn = document.getElementById('btn-save-scenario');
  if (saveBtn) {
    saveBtn.addEventListener('click', saveScenario);
  }
}

async function triggerSimulation() {
  if (!window.currentProjectId) return;

  const labor = parseFloat(document.getElementById('sim-labor').value) || 0;
  const weather = parseInt(document.getElementById('sim-weather').value) || 0;
  const materials = parseInt(document.getElementById('sim-materials').value) || 0;
  const budget = parseFloat(document.getElementById('sim-budget').value) || 0;
  const efficiency = parseFloat(document.getElementById('sim-efficiency').value) || 100;

  const btn = document.getElementById('btn-run-simulation');
  if (btn) {
    btn.disabled = true;
    btn.textContent = 'Simulating Dynamics...';
  }

  try {
    const payload = {
      laborVariancePct: labor,
      severeWeatherDays: weather,
      materialDelayDays: materials,
      budgetAccelerationAmount: budget,
      subcontractorEfficiencyPct: efficiency
    };

    const res = await api.runWhatIf(window.currentProjectId, payload);
    currentSimulationResult = res;
    renderSimulationResults(res);
  } catch (err) {
    showToast(err.message, 'error');
  } finally {
    if (btn) {
      btn.disabled = false;
      btn.innerHTML = '<span>⚡ Run What-If Simulation</span>';
    }
  }
}

function renderSimulationResults(res) {
  const container = document.getElementById('simulation-results-container');
  if (!container) return;

  const riskDelta = res.riskChangeDelta;
  const riskColor = riskDelta > 0 ? '#ef4444' : (riskDelta < 0 ? '#10b981' : '#94a3b8');
  const riskBadgeClass = riskDelta > 0 ? 'badge-rose' : (riskDelta < 0 ? 'badge-emerald' : 'badge-subtle');
  const riskSign = riskDelta > 0 ? `+${riskDelta}` : `${riskDelta}`;

  const delayDelta = res.netDelayChangeDays;
  const delayColor = delayDelta > 0 ? '#ef4444' : (delayDelta < 0 ? '#10b981' : '#94a3b8');
  const delaySign = delayDelta > 0 ? `+${delayDelta} Days` : (delayDelta < 0 ? `${delayDelta} Days` : '0 Days');

  const costImpact = res.simulatedCostImpact;
  const costColor = costImpact > 0 ? '#f59e0b' : (costImpact < 0 ? '#10b981' : '#94a3b8');
  const costFormatted = (costImpact >= 0 ? `+$${costImpact.toLocaleString()}` : `-$${Math.abs(costImpact).toLocaleString()}`);

  container.innerHTML = `
    <div class="sim-kpi-grid">
      <div class="sim-kpi-card">
        <div class="sim-kpi-label">Projected Completion</div>
        <div class="sim-kpi-value" style="font-size: 16px;">${res.projectedCompletionDate}</div>
        <div style="font-size: 11px; margin-top: 4px; color: ${delayColor}; font-weight: 700;">
          Schedule Shift: ${delaySign}
        </div>
      </div>

      <div class="sim-kpi-card">
        <div class="sim-kpi-label">Simulated Risk Score</div>
        <div class="sim-kpi-value" style="color: ${riskColor};">
          ${res.simulatedRiskScore}/100
        </div>
        <div style="margin-top: 4px;">
          <span class="badge ${riskBadgeClass}">${riskSign} Risk Points</span>
        </div>
      </div>

      <div class="sim-kpi-card">
        <div class="sim-kpi-label">Est. Financial Cost Delta</div>
        <div class="sim-kpi-value" style="color: ${costColor}; font-size: 16px;">
          ${costFormatted}
        </div>
        <div style="font-size: 11px; margin-top: 4px; color: var(--text-muted);">
          Overhead & Expedite Impact
        </div>
      </div>

      <div class="sim-kpi-card">
        <div class="sim-kpi-label">Simulated Velocity (SPI)</div>
        <div class="sim-kpi-value" style="color: ${res.simulatedSPI >= 1.0 ? '#10b981' : '#f59e0b'};">
          ${res.simulatedSPI.toFixed(2)}
        </div>
        <div style="font-size: 11px; margin-top: 4px; color: var(--text-muted);">
          CPI: ${res.simulatedCPI.toFixed(2)}
        </div>
      </div>
    </div>

    <div class="sim-narrative">
      <strong>Scenario Summary:</strong> ${res.summaryAnalysis}
    </div>
  `;
}

async function saveScenario() {
  if (!window.currentProjectId || !currentSimulationResult) {
    showToast('Run a simulation first before saving.', 'warning');
    return;
  }

  const name = prompt('Enter a name for this contingency scenario:', 'Contingency Acceleration Plan A');
  if (!name) return;

  try {
    await api.saveScenario(window.currentProjectId, {
      scenarioName: name,
      simulationResult: currentSimulationResult,
      savedAt: new Date().toISOString()
    });
    showToast(`Scenario "${name}" saved to project contingency repository!`, 'success');
  } catch (err) {
    showToast(err.message, 'error');
  }
}
