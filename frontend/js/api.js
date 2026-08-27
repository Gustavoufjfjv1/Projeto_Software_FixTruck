const API_BASE = localStorage.getItem('fixtruck_api') || 'http://127.0.0.1:5000';

const Api = {
  getToken() {
    return localStorage.getItem('fixtruck_token');
  },

  setSession(token, empresa) {
    localStorage.setItem('fixtruck_token', token);
    if (empresa) {
      localStorage.setItem('fixtruck_empresa', JSON.stringify(empresa));
    }
  },

  clearSession() {
    localStorage.removeItem('fixtruck_token');
    localStorage.removeItem('fixtruck_empresa');
  },

  getEmpresa() {
    try {
      return JSON.parse(localStorage.getItem('fixtruck_empresa') || 'null');
    } catch {
      return null;
    }
  },

  isAuthenticated() {
    return Boolean(this.getToken());
  },

  requireAuth() {
    if (!this.isAuthenticated()) {
      window.location.href = 'login.html';
      return false;
    }
    return true;
  },

  async request(path, options = {}) {
    const headers = {
      'Content-Type': 'application/json',
      ...(options.headers || {}),
    };
    const token = this.getToken();
    if (token) headers.Authorization = `Bearer ${token}`;

    const res = await fetch(`${API_BASE}${path}`, {
      ...options,
      headers,
    });

    let data = null;
    const text = await res.text();
    if (text) {
      try {
        data = JSON.parse(text);
      } catch {
        data = { erro: text };
      }
    }

    if (res.status === 401 && !path.startsWith('/api/auth/login')) {
      this.clearSession();
      window.location.href = 'login.html';
      throw new Error('Não autenticado');
    }

    if (!res.ok) {
      const err = new Error((data && data.erro) || 'Erro na requisição');
      err.status = res.status;
      err.data = data;
      throw err;
    }
    return data;
  },

  get(path) {
    return this.request(path);
  },

  post(path, body) {
    return this.request(path, { method: 'POST', body: JSON.stringify(body || {}) });
  },

  put(path, body) {
    return this.request(path, { method: 'PUT', body: JSON.stringify(body || {}) });
  },

  patch(path, body) {
    return this.request(path, { method: 'PATCH', body: JSON.stringify(body || {}) });
  },
};

function showFlash(message, type = 'success') {
  let container = document.querySelector('.flash-container');
  if (!container) {
    container = document.createElement('div');
    container.className = 'flash-container';
    document.body.prepend(container);
  }
  const el = document.createElement('div');
  el.className = `flash flash-${type}`;
  el.textContent = message;
  container.appendChild(el);
  setTimeout(() => {
    el.style.opacity = '0';
    el.style.transition = 'opacity .5s ease';
    setTimeout(() => el.remove(), 500);
  }, 4000);
}

function qs(name) {
  return new URLSearchParams(window.location.search).get(name);
}

// Volta para a página de onde o usuário realmente veio (via document.referrer),
// em vez de sempre mandar para um hub fixo. Cai no fallback se vier de fora do app.
function voltarPara(fallback) {
  try {
    const ref = document.referrer;
    if (ref && ref.indexOf(window.location.origin + '/') === 0) {
      const refUrl = new URL(ref);
      if (refUrl.pathname !== window.location.pathname) {
        return ref;
      }
    }
  } catch (e) {}
  return fallback;
}

function statusBadge(status) {
  if (status === 'aberta') {
    return '<span class="badge badge-red"><span class="status-dot dot-red"></span>Aberta</span>';
  }
  if (status === 'em_atendimento') {
    return '<span class="badge badge-orange"><span class="status-dot dot-orange"></span>Em Atendimento</span>';
  }
  if (status === 'resolvido') {
    return '<span class="badge badge-green"><span class="status-dot dot-green"></span>Resolvido</span>';
  }
  return `<span class="badge">${status || '-'}</span>`;
}

function formatDate(value) {
  if (!value) return '-';
  return String(value).slice(0, 16);
}
