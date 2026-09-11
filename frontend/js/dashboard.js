/**
 * BuildPulse Dashboard Main Controller
 */

window.currentProjectId = null;
window.currentProjectData = null;

document.addEventListener('DOMContentLoaded', async () => {
  // 1. Auth Guard
  const token = getAuthToken();
  if (!token) {
    window.location.href = '/login';
    return;
  }

  // 2. Load User Profile
  try {
    const user = await api.getMe();
    setCurrentUser(user);
    renderUserBadge(user);
  } catch (err) {
    setAuthToken(null);
    window.location.href = '/login';
    return;
  }

  // 3. Database status check
  try {
    const status = await api.getStatus();
    const dbBadge = document.getElementById('db-status-badge');
    if (dbBadge) {
      if (status.isFirebaseLive) {
        dbBadge.className = 'badge badge-emerald';
        dbBadge.innerHTML = '☁️ Firebase Firestore Live';
      } else {
        dbBadge.className = 'badge badge-amber';
        dbBadge.innerHTML = '⚡ Local Firestore Engine';
      }
    }
  } catch (e) {
    console.error('Status check error:', e);
  }

  // 4. Initialize What-If Simulator listeners
  initWhatIfSimulator();

  // 5. Setup Project Switcher & Load Data
  await loadProjects();

  // 6. Setup Modal listeners
  setupModalListeners();

  // Logout button listener
  const logoutBtn = document.getElementById('btn-logout');
  if (logoutBtn) {
    logoutBtn.addEventListener('click', () => {
      setAuthToken(null);
      setCurrentUser(null);
      showToast('Logged out successfully.', 'info');
      setTimeout(() => window.location.href = '/login', 400);
    });
  }
});

function renderUserBadge(user) {
  const nameEl = document.getElementById('nav-user-name');
  const roleEl = document.getElementById('nav-user-role');
  const avatarEl = document.getElementById('nav-user-avatar');

  if (nameEl) nameEl.textContent = user.fullName;
  if (roleEl) roleEl.textContent = `${user.role} • ${user.company || ''}`;
  if (avatarEl) {
    const initials = user.fullName.split(' ').map(n => n[0]).join('').toUpperCase().substring(0, 2);
    avatarEl.textContent = initials || 'BP';
  }
}

async function loadProjects() {
  try {
    const projects = await api.getProjects();
    const selectEl = document.getElementById('project-select');
    if (!selectEl) return;

    selectEl.innerHTML = projects.map(p => `
      <option value="${p.id}">${p.name} (${p.code})</option>
    `).join('');

    // Default select first project or previously selected
    const selectedId = localStorage.getItem('buildpulse_active_project') || (projects[0] && projects[0].id);
    if (selectedId) {
      selectEl.value = selectedId;
      await selectProject(selectedId);
    }

    selectEl.addEventListener('change', async (e) => {
      await selectProject(e.target.value);
    });
  } catch (err) {
    showToast('Failed to load projects: ' + err.message, 'error');
  }
}

async function selectProject(projectId) {
  window.currentProjectId = projectId;
  localStorage.setItem('buildpulse_active_project', projectId);

  try {
    // Fetch full project details and risk score in parallel
    const [project, risk] = await Promise.all([
      api.getProject(projectId),
      api.getProjectRisk(projectId)
    ]);

    window.currentProjectData = project;
    renderProjectHeader(project);
    renderProjectMetrics(project, risk);
    renderSCurveChart(project);
    renderPhasesList(project);
    renderRiskGauge(risk);

    // Run baseline simulation
    triggerSimulation();
  } catch (err) {
    showToast('Failed to load project details: ' + err.message, 'error');
  }
}

function renderProjectHeader(project) {
  const titleEl = document.getElementById('project-header-title');
  const metaEl = document.getElementById('project-header-meta');

  if (titleEl) {
    titleEl.innerHTML = `
      <span>${project.name}</span>
      <span class="badge badge-amber">${project.type}</span>
    `;
  }

  if (metaEl) {
    metaEl.innerHTML = `
      <div class="project-meta-item"><span>📍</span> <span>${project.location}</span></div>
      <div class="project-meta-item"><span>🏗️</span> <span>Prime: <strong>${project.contractor}</strong></span></div>
      <div class="project-meta-item"><span>👤</span> <span>Manager: <strong>${project.manager}</strong></span></div>
      <div class="project-meta-item"><span>🎯</span> <span>Target Handover: <strong>${project.targetCompletionDate}</strong></span></div>
    `;
  }
}

function renderProjectMetrics(project, risk) {
  // 1. Progress Metric
  const progVal = document.getElementById('metric-progress-val');
  const progSub = document.getElementById('metric-progress-sub');
  const progBar = document.getElementById('metric-progress-bar');
  const delta = project.actualProgress - project.plannedProgress;
  const deltaSign = delta >= 0 ? `+${delta.toFixed(1)}%` : `${delta.toFixed(1)}%`;
  const deltaBadgeClass = delta >= 0 ? 'badge-emerald' : 'badge-amber';

  if (progVal) progVal.innerHTML = `${project.actualProgress}% <span style="font-size: 14px; font-weight: 500; color: var(--text-muted);">/ ${project.plannedProgress}% Plan</span>`;
  if (progSub) progSub.innerHTML = `<span class="badge ${deltaBadgeClass}">${deltaSign} Variance</span> <span>Target ${project.plannedProgress}%</span>`;
  if (progBar) progBar.style.width = `${Math.min(100, project.actualProgress)}%`;

  // 2. Budget Health Metric
  const budgetVal = document.getElementById('metric-budget-val');
  const budgetSub = document.getElementById('metric-budget-sub');
  const cpiBadgeClass = risk.costPerformanceIndex >= 1.0 ? 'badge-emerald' : 'badge-amber';

  if (budgetVal) {
    const spentM = (project.spentBudget / 1000000).toFixed(1);
    const totalM = (project.totalBudget / 1000000).toFixed(1);
    budgetVal.innerHTML = `$${spentM}M <span style="font-size: 14px; font-weight: 500; color: var(--text-muted);">/ $${totalM}M</span>`;
  }
  if (budgetSub) {
    budgetSub.innerHTML = `<span class="badge ${cpiBadgeClass}">CPI: ${risk.costPerformanceIndex.toFixed(2)}</span> <span>${((project.spentBudget / project.totalBudget) * 100).toFixed(1)}% Spent</span>`;
  }

  // 3. Schedule Health Metric
  const schedVal = document.getElementById('metric-schedule-val');
  const schedSub = document.getElementById('metric-schedule-sub');
  const spiBadgeClass = risk.schedulePerformanceIndex >= 1.0 ? 'badge-emerald' : 'badge-amber';

  if (schedVal) {
    schedVal.innerHTML = `${risk.predictedCompletionDate}`;
  }
  if (schedSub) {
    const delayDays = risk.projectedDelayDays;
    const delaySign = delayDays > 0 ? `+${delayDays}d Slippage` : 'On Schedule';
    schedSub.innerHTML = `<span class="badge ${delayDays > 0 ? 'badge-rose' : 'badge-emerald'}">${delaySign}</span> <span class="badge ${spiBadgeClass}">SPI: ${risk.schedulePerformanceIndex.toFixed(2)}</span>`;
  }

  // 4. Resources Metric
  const resVal = document.getElementById('metric-resources-val');
  const resSub = document.getElementById('metric-resources-sub');

  if (resVal) {
    resVal.innerHTML = `${project.workerCount} <span style="font-size: 14px; font-weight: 500; color: var(--text-muted);">Workers</span>`;
  }
  if (resSub) {
    resSub.innerHTML = `<span class="badge badge-cyan">${project.equipmentCount} Equipment</span> <span class="badge badge-emerald">🛡️ ${project.safetyIncidentFreeDays}d Incident-Free</span>`;
  }
}

function renderSCurveChart(project) {
  const container = document.getElementById('s-curve-chart');
  if (!container) return;

  const history = project.historyProgress || [];
  if (history.length === 0) return;

  // Chart dimensions
  const width = 600;
  const height = 220;
  const padLeft = 40;
  const padRight = 20;
  const padTop = 20;
  const padBottom = 30;

  const chartW = width - padLeft - padRight;
  const chartH = height - padTop - padBottom;

  const n = history.length;
  const xStep = chartW / Math.max(1, n - 1);

  // Convert points to coordinates
  const plannedPoints = history.map((pt, i) => {
    const x = padLeft + i * xStep;
    const y = padTop + chartH - (pt.planned / 100) * chartH;
    return { x, y, val: pt.planned, month: pt.month };
  });

  const actualPoints = history.map((pt, i) => {
    const x = padLeft + i * xStep;
    const y = padTop + chartH - (pt.actual / 100) * chartH;
    return { x, y, val: pt.actual, month: pt.month };
  });

  // SVG Path generator
  const createPathD = (pts) => pts.reduce((acc, p, i) => `${acc} ${i === 0 ? 'M' : 'L'} ${p.x.toFixed(1)} ${p.y.toFixed(1)}`, '');

  const plannedD = createPathD(plannedPoints);
  const actualD = createPathD(actualPoints);

  // Area under actual
  const lastX = actualPoints[actualPoints.length - 1].x;
  const firstX = actualPoints[0].x;
  const bottomY = padTop + chartH;
  const areaActualD = `${actualD} L ${lastX} ${bottomY} L ${firstX} ${bottomY} Z`;

  // Grid lines
  const gridLines = [0, 25, 50, 75, 100].map(pct => {
    const y = padTop + chartH - (pct / 100) * chartH;
    return `
      <line x1="${padLeft}" y1="${y}" x2="${width - padRight}" y2="${y}" stroke="rgba(255, 255, 255, 0.06)" stroke-dasharray="3,3"/>
      <text x="${padLeft - 8}" y="${y + 4}" fill="#64748b" font-size="10" text-anchor="end" font-family="var(--font-mono)">${pct}%</text>
    `;
  }).join('');

  // X Axis labels
  const xLabels = history.map((pt, i) => {
    const x = padLeft + i * xStep;
    return `<text x="${x}" y="${height - 8}" fill="#94a3b8" font-size="11" text-anchor="middle">${pt.month}</text>`;
  }).join('');

  container.innerHTML = `
    <svg viewBox="0 0 ${width} ${height}" class="s-curve-svg">
      <defs>
        <linearGradient id="actual-area-grad" x1="0" y1="0" x2="0" y2="1">
          <stop offset="0%" stop-color="#10b981" stop-opacity="0.3"/>
          <stop offset="100%" stop-color="#10b981" stop-opacity="0.0"/>
        </linearGradient>
      </defs>

      <!-- Grid -->
      ${gridLines}
      ${xLabels}

      <!-- Actual Area Fill -->
      <path d="${areaActualD}" fill="url(#actual-area-grad)"/>

      <!-- Planned Baseline Curve (Amber dashed) -->
      <path d="${plannedD}" fill="none" stroke="#f59e0b" stroke-width="2.5" stroke-dasharray="6,4" stroke-linecap="round"/>

      <!-- Actual Progress Curve (Emerald Solid) -->
      <path d="${actualD}" fill="none" stroke="#10b981" stroke-width="3" stroke-linecap="round"/>

      <!-- Dots for Planned -->
      ${plannedPoints.map(p => `
        <circle cx="${p.x}" cy="${p.y}" r="3.5" fill="#f59e0b"/>
      `).join('')}

      <!-- Dots for Actual -->
      ${actualPoints.map(p => `
        <circle cx="${p.x}" cy="${p.y}" r="4.5" fill="#10b981" stroke="#0a0e17" stroke-width="2"/>
      `).join('')}
    </svg>
  `;
}

function renderPhasesList(project) {
  const container = document.getElementById('phases-list-container');
  if (!container) return;

  const phases = project.phases || [];

  container.innerHTML = phases.map(phase => {
    let statusBadge = '';
    let barColor = '#10b981';

    if (phase.status === 'completed') {
      statusBadge = '<span class="badge badge-emerald">Completed</span>';
      barColor = '#10b981';
    } else if (phase.status === 'delayed') {
      statusBadge = `<span class="badge badge-rose">Delayed (+${phase.delayDays}d)</span>`;
      barColor = '#ef4444';
    } else if (phase.status === 'in_progress') {
      statusBadge = '<span class="badge badge-cyan">In Progress</span>';
      barColor = '#06b6d4';
    } else {
      statusBadge = '<span class="badge badge-subtle">Pending</span>';
      barColor = '#64748b';
    }

    return `
      <div class="phase-item">
        <div class="phase-info">
          <div class="phase-name">
            <span>${phase.name}</span>
            ${phase.criticalPath ? '<span class="badge badge-rose" style="font-size: 10px;">Critical Path</span>' : ''}
          </div>
          <div class="phase-sub">
            <span>Contractor: <strong>${phase.contractor}</strong></span>
            <span>Weight: <strong>${phase.weight}%</strong></span>
            <span>Target: <strong>${phase.plannedEnd}</strong></span>
          </div>
        </div>

        <div class="flex items-center gap-4">
          <div class="phase-progress-wrap">
            <div class="phase-progress-numbers">
              <span style="color: ${barColor}; font-weight: 700;">${phase.actualProgress}%</span>
              <span style="color: var(--text-muted);">${phase.plannedProgress}% Plan</span>
            </div>
            <div class="phase-bar">
              <div class="phase-bar-fill" style="width: ${phase.actualProgress}%; background: ${barColor};"></div>
            </div>
          </div>

          <div style="min-width: 90px; text-align: right;">
            ${statusBadge}
          </div>

          <button class="btn btn-outline btn-sm" onclick="openUpdateModal('${phase.id}', '${phase.name.replace(/'/g, "\\'")}', ${phase.actualProgress})">
            Update %
          </button>
        </div>
      </div>
    `;
  }).join('');
}

// Modal logic for updating milestone progress
window.openUpdateModal = function(phaseId, phaseName, currentProgress) {
  const modal = document.getElementById('update-modal');
  const titleEl = document.getElementById('modal-phase-name');
  const inputEl = document.getElementById('modal-progress-input');
  const sliderEl = document.getElementById('modal-progress-slider');
  const formEl = document.getElementById('modal-update-form');

  if (!modal) return;

  titleEl.textContent = phaseName;
  inputEl.value = currentProgress;
  sliderEl.value = currentProgress;

  modal.dataset.phaseId = phaseId;
  modal.classList.add('active');
};

function setupModalListeners() {
  const modal = document.getElementById('update-modal');
  const closeBtn = document.getElementById('modal-close-btn');
  const cancelBtn = document.getElementById('modal-cancel-btn');
  const inputEl = document.getElementById('modal-progress-input');
  const sliderEl = document.getElementById('modal-progress-slider');
  const formEl = document.getElementById('modal-update-form');

  const closeModal = () => {
    if (modal) modal.classList.remove('active');
  };

  if (closeBtn) closeBtn.addEventListener('click', closeModal);
  if (cancelBtn) cancelBtn.addEventListener('click', closeModal);

  if (sliderEl && inputEl) {
    sliderEl.addEventListener('input', (e) => inputEl.value = e.target.value);
    inputEl.addEventListener('input', (e) => sliderEl.value = e.target.value);
  }

  if (formEl) {
    formEl.addEventListener('submit', async (e) => {
      e.preventDefault();
      const phaseId = modal.dataset.phaseId;
      const progress = parseFloat(inputEl.value);

      if (!window.currentProjectId || !phaseId) return;

      try {
        const btn = formEl.querySelector('button[type="submit"]');
        btn.disabled = true;
        btn.textContent = 'Saving...';

        const res = await api.updatePhaseProgress(window.currentProjectId, phaseId, progress);
        showToast(`Progress updated to ${progress}%! Overall completion is now ${res.newOverallProgress}%`, 'success');
        closeModal();

        // Refresh project and risk
        await selectProject(window.currentProjectId);
      } catch (err) {
        showToast('Error saving progress: ' + err.message, 'error');
      } finally {
        const btn = formEl.querySelector('button[type="submit"]');
        btn.disabled = false;
        btn.textContent = 'Save Progress';
      }
    });
  }
}
