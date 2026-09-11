/**
 * BuildPulse Delay Risk Gauge & Factor Breakdown Visualization
 */

function getRiskTierColor(score) {
  if (score < 30) return { primary: '#10b981', gradient: 'url(#gauge-green)', textClass: 'badge-emerald', label: 'Low Delay Risk' };
  if (score < 55) return { primary: '#f59e0b', gradient: 'url(#gauge-amber)', textClass: 'badge-amber', label: 'Moderate Delay Risk' };
  if (score < 75) return { primary: '#f97316', gradient: 'url(#gauge-orange)', textClass: 'badge-amber', label: 'High Delay Risk' };
  return { primary: '#ef4444', gradient: 'url(#gauge-red)', textClass: 'badge-rose', label: 'Critical Delay Risk' };
}

function renderRiskGauge(riskData) {
  const container = document.getElementById('risk-gauge-container');
  if (!container) return;

  const score = riskData.overallRiskScore;
  const tierInfo = getRiskTierColor(score);

  // SVG Gauge calculations (Semi-circle, radius 80)
  // Arc length for 180 degrees with r=80 is pi * 80 ≈ 251.3
  const r = 80;
  const circumference = Math.PI * r;
  const strokeDashoffset = circumference - (score / 100) * circumference;

  container.innerHTML = `
    <div class="gauge-svg-container">
      <svg class="gauge-svg" viewBox="0 0 200 115">
        <defs>
          <linearGradient id="gauge-bg" x1="0%" y1="0%" x2="100%" y2="0%">
            <stop offset="0%" stop-color="#10b981" stop-opacity="0.2"/>
            <stop offset="50%" stop-color="#f59e0b" stop-opacity="0.2"/>
            <stop offset="100%" stop-color="#ef4444" stop-opacity="0.2"/>
          </linearGradient>
          <linearGradient id="gauge-green" x1="0%" y1="0%" x2="100%" y2="0%">
            <stop offset="0%" stop-color="#10b981"/>
            <stop offset="100%" stop-color="#34d399"/>
          </linearGradient>
          <linearGradient id="gauge-amber" x1="0%" y1="0%" x2="100%" y2="0%">
            <stop offset="0%" stop-color="#f59e0b"/>
            <stop offset="100%" stop-color="#fbbf24"/>
          </linearGradient>
          <linearGradient id="gauge-orange" x1="0%" y1="0%" x2="100%" y2="0%">
            <stop offset="0%" stop-color="#f97316"/>
            <stop offset="100%" stop-color="#fb923c"/>
          </linearGradient>
          <linearGradient id="gauge-red" x1="0%" y1="0%" x2="100%" y2="0%">
            <stop offset="0%" stop-color="#ef4444"/>
            <stop offset="100%" stop-color="#f87171"/>
          </linearGradient>
        </defs>

        <!-- Background Track -->
        <path d="M 20 100 A 80 80 0 0 1 180 100" 
              fill="none" 
              stroke="rgba(255, 255, 255, 0.08)" 
              stroke-width="16" 
              stroke-linecap="round"/>

        <!-- Colored Progress Arc -->
        <path d="M 20 100 A 80 80 0 0 1 180 100" 
              fill="none" 
              stroke="${tierInfo.primary}" 
              stroke-width="16" 
              stroke-linecap="round"
              stroke-dasharray="${circumference}"
              stroke-dashoffset="${strokeDashoffset}"
              style="transition: stroke-dashoffset 1s cubic-bezier(0.16, 1, 0.3, 1), stroke 0.5s ease;"/>
      </svg>

      <div class="gauge-center-text">
        <div class="gauge-score" style="color: ${tierInfo.primary}">${score}</div>
        <div class="badge ${tierInfo.textClass} gauge-tier-badge">${tierInfo.label}</div>
      </div>
    </div>
  `;

  // Render Factor Breakdown
  const factorContainer = document.getElementById('risk-factors-container');
  if (factorContainer && riskData.factors) {
    factorContainer.innerHTML = riskData.factors.map(factor => {
      let barColor = '#10b981';
      if (factor.score >= 60) barColor = '#ef4444';
      else if (factor.score >= 35) barColor = '#f59e0b';

      return `
        <div class="factor-item">
          <div class="factor-header">
            <span>${factor.name}</span>
            <span style="color: ${barColor}">${factor.score.toFixed(0)}/100 (${factor.impact})</span>
          </div>
          <div class="factor-bar-bg">
            <div class="factor-bar-fill" style="width: ${Math.min(100, factor.score)}%; background: ${barColor};"></div>
          </div>
          <div style="font-size: 11px; color: var(--text-muted); margin-top: 2px;">${factor.description}</div>
        </div>
      `;
    }).join('');
  }

  // Render AI Recommendations
  const recContainer = document.getElementById('risk-recommendations-container');
  if (recContainer && riskData.recommendations) {
    recContainer.innerHTML = riskData.recommendations.map(rec => `
      <div class="rec-card">
        <div class="rec-header">
          <span class="rec-title">⚡ AI Mitigation: ${rec.priority} Priority</span>
          <span class="badge badge-emerald">Recover +${rec.recoveryPotentialDays} Days</span>
        </div>
        <div class="rec-body">${rec.action}</div>
        ${rec.estimatedCost && rec.estimatedCost !== '$0' ? `<div style="font-size: 11px; color: var(--text-muted); margin-top: 4px;">Est. Investment: <strong style="color: #f8fafc;">${rec.estimatedCost}</strong></div>` : ''}
      </div>
    `).join('');
  }
}
