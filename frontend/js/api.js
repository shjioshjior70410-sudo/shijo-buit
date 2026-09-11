/**
 * BuildPulse API Client Layer
 * Handles authentication headers, error notifications, and REST endpoints.
 */

const API_BASE = window.location.origin;

function getAuthToken() {
  return localStorage.getItem('buildpulse_token');
}

function setAuthToken(token) {
  if (token) {
    localStorage.setItem('buildpulse_token', token);
  } else {
    localStorage.removeItem('buildpulse_token');
  }
}

function getCurrentUser() {
  const userStr = localStorage.getItem('buildpulse_user');
  try {
    return userStr ? JSON.parse(userStr) : null;
  } catch (e) {
    return null;
  }
}

function setCurrentUser(user) {
  if (user) {
    localStorage.setItem('buildpulse_user', JSON.stringify(user));
  } else {
    localStorage.removeItem('buildpulse_user');
  }
}

function showToast(message, type = 'info') {
  let container = document.getElementById('toast-container');
  if (!container) {
    container = document.createElement('div');
    container.id = 'toast-container';
    document.body.appendChild(container);
  }

  const toast = document.createElement('div');
  toast.className = `toast toast-${type}`;
  toast.innerHTML = `
    <span>${type === 'success' ? '✓' : type === 'error' ? '✕' : 'ℹ'}</span>
    <div>${message}</div>
  `;
  container.appendChild(toast);

  setTimeout(() => {
    toast.style.opacity = '0';
    toast.style.transform = 'translateY(10px)';
    toast.style.transition = 'all 0.3s ease';
    setTimeout(() => toast.remove(), 300);
  }, 4000);
}

async function apiRequest(endpoint, options = {}) {
  const headers = {
    'Content-Type': 'application/json',
    ...(options.headers || {})
  };

  const token = getAuthToken();
  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }

  try {
    const response = await fetch(`${API_BASE}${endpoint}`, {
      ...options,
      headers
    });

    if (response.status === 401) {
      // Clear token and redirect to login if not already there
      setAuthToken(null);
      setCurrentUser(null);
      if (!window.location.pathname.includes('login')) {
        window.location.href = '/login';
      }
      throw new Error('Session expired. Please log in again.');
    }

    const data = await response.json();
    if (!response.ok) {
      throw new Error(data.detail || 'An error occurred during API request.');
    }
    return data;
  } catch (err) {
    console.error(`API Error [${endpoint}]:`, err);
    throw err;
  }
}

// API Methods
const api = {
  // Auth
  login: (credentials) => apiRequest('/api/auth/login', { method: 'POST', body: JSON.stringify(credentials) }),
  register: (userData) => apiRequest('/api/auth/register', { method: 'POST', body: JSON.stringify(userData) }),
  demoLogin: (role) => apiRequest(`/api/auth/demo-login/${role}`, { method: 'POST' }),
  getMe: () => apiRequest('/api/auth/me'),

  // Status & Health
  getStatus: () => apiRequest('/api/status'),

  // Projects
  getProjects: () => apiRequest('/api/projects'),
  getProject: (id) => apiRequest(`/api/projects/${id}`),
  getProjectRisk: (id) => apiRequest(`/api/projects/${id}/risk`),
  updatePhaseProgress: (projectId, phaseId, actualProgress) => 
    apiRequest(`/api/projects/${projectId}/phases/${phaseId}`, {
      method: 'POST',
      body: JSON.stringify({ actualProgress })
    }),
  runWhatIf: (projectId, scenario) => 
    apiRequest(`/api/projects/${projectId}/what-if`, {
      method: 'POST',
      body: JSON.stringify(scenario)
    }),
  saveScenario: (projectId, scenarioData) =>
    apiRequest(`/api/projects/${projectId}/scenarios`, {
      method: 'POST',
      body: JSON.stringify(scenarioData)
    })
};
