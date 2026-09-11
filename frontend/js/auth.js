/**
 * BuildPulse Authentication Controller
 */

document.addEventListener('DOMContentLoaded', () => {
  // If already authenticated and on login page, redirect to dashboard
  const token = getAuthToken();
  if (token && window.location.pathname.includes('login')) {
    // Check if token is valid
    api.getMe().then(() => {
      window.location.href = '/';
    }).catch(() => {
      setAuthToken(null);
    });
  }

  // Tabs toggle
  const tabLogin = document.getElementById('tab-login');
  const tabRegister = document.getElementById('tab-register');
  const formLogin = document.getElementById('form-login');
  const formRegister = document.getElementById('form-register');

  if (tabLogin && tabRegister) {
    tabLogin.addEventListener('click', () => {
      tabLogin.classList.add('active');
      tabRegister.classList.remove('active');
      formLogin.classList.remove('hidden');
      formRegister.classList.add('hidden');
    });

    tabRegister.addEventListener('click', () => {
      tabRegister.classList.add('active');
      tabLogin.classList.remove('active');
      formRegister.classList.remove('hidden');
      formLogin.classList.add('hidden');
    });
  }

  // Handle standard login
  if (formLogin) {
    formLogin.addEventListener('submit', async (e) => {
      e.preventDefault();
      const email = document.getElementById('login-email').value;
      const password = document.getElementById('login-password').value;
      const btn = formLogin.querySelector('button[type="submit"]');

      try {
        btn.disabled = true;
        btn.textContent = 'Authenticating...';
        const res = await api.login({ email, password });
        setAuthToken(res.access_token);
        setCurrentUser(res.user);
        showToast('Login successful! Redirecting to operations center...', 'success');
        setTimeout(() => window.location.href = '/', 600);
      } catch (err) {
        showToast(err.message, 'error');
        btn.disabled = false;
        btn.textContent = 'Sign In to Platform';
      }
    });
  }

  // Handle registration
  if (formRegister) {
    formRegister.addEventListener('submit', async (e) => {
      e.preventDefault();
      const fullName = document.getElementById('reg-name').value;
      const email = document.getElementById('reg-email').value;
      const role = document.getElementById('reg-role').value;
      const company = document.getElementById('reg-company').value;
      const password = document.getElementById('reg-password').value;
      const btn = formRegister.querySelector('button[type="submit"]');

      try {
        btn.disabled = true;
        btn.textContent = 'Creating Account...';
        const res = await api.register({ fullName, email, role, company, password });
        setAuthToken(res.access_token);
        setCurrentUser(res.user);
        showToast('Account registered successfully! Loading workspace...', 'success');
        setTimeout(() => window.location.href = '/', 600);
      } catch (err) {
        showToast(err.message, 'error');
        btn.disabled = false;
        btn.textContent = 'Create Account';
      }
    });
  }

  // Quick Demo Login Buttons
  const demoManagerBtn = document.getElementById('demo-manager-btn');
  const demoEngineerBtn = document.getElementById('demo-engineer-btn');

  if (demoManagerBtn) {
    demoManagerBtn.addEventListener('click', async () => {
      try {
        demoManagerBtn.disabled = true;
        demoManagerBtn.textContent = 'Logging in...';
        const res = await api.demoLogin('manager');
        setAuthToken(res.access_token);
        setCurrentUser(res.user);
        showToast('Authenticated as Elena Rostova (Project Manager)', 'success');
        setTimeout(() => window.location.href = '/', 500);
      } catch (err) {
        showToast(err.message, 'error');
        demoManagerBtn.disabled = false;
        demoManagerBtn.textContent = '⚡ Elena Rostova (Project Manager)';
      }
    });
  }

  if (demoEngineerBtn) {
    demoEngineerBtn.addEventListener('click', async () => {
      try {
        demoEngineerBtn.disabled = true;
        demoEngineerBtn.textContent = 'Logging in...';
        const res = await api.demoLogin('engineer');
        setAuthToken(res.access_token);
        setCurrentUser(res.user);
        showToast('Authenticated as Marcus Sterling (Site Superintendent)', 'success');
        setTimeout(() => window.location.href = '/', 500);
      } catch (err) {
        showToast(err.message, 'error');
        demoEngineerBtn.disabled = false;
        demoEngineerBtn.textContent = '⚡ Marcus Sterling (Site Superintendent)';
      }
    });
  }
});
