const API_BASE = localStorage.getItem('fixtruck_api') || 'http://127.0.0.1:5000';

// Páginas do motorista declaram <body data-papel="motorista">: usam outro token e outra tela de login.
const Api = {
  papel() {
    return document.body && document.body.dataset.papel === 'motorista' ? 'motorista' : 'empresa';
  },

  loginPage() {
    return this.papel() === 'motorista' ? 'motorista_login.html' : 'login.html';
  },

  getToken() {
    return localStorage.getItem(this.papel() === 'motorista' ? 'fixtruck_motorista_token' : 'fixtruck_token');
  },

  setSession(token, empresa) {
    localStorage.setItem('fixtruck_token', token);
    if (empresa) {
      localStorage.setItem('fixtruck_empresa', JSON.stringify(empresa));
    }
  },

  setSessionMotorista(token, motorista, empresaNome) {
    localStorage.setItem('fixtruck_motorista_token', token);
    if (motorista) localStorage.setItem('fixtruck_motorista', JSON.stringify(motorista));
    if (empresaNome != null) localStorage.setItem('fixtruck_motorista_empresa', empresaNome);
  },

  getMotorista() {
    try {
      return JSON.parse(localStorage.getItem('fixtruck_motorista') || 'null');
    } catch {
      return null;
    }
  },

  clearSession() {
    if (this.papel() === 'motorista') {
      localStorage.removeItem('fixtruck_motorista_token');
      localStorage.removeItem('fixtruck_motorista');
      localStorage.removeItem('fixtruck_motorista_empresa');
      return;
    }
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
      window.location.href = this.loginPage();
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

    const rotaDeLogin = path.startsWith('/api/auth/login') || path.startsWith('/api/motorista/login')
      || path.startsWith('/api/motorista/trocar-senha');
    if (res.status === 401 && !rotaDeLogin) {
      this.clearSession();
      window.location.href = this.loginPage();
      throw new Error('Não autenticado');
    }

    if (res.status === 403 && data && data.trocar_senha) {
      window.location.href = 'motorista_trocar_senha.html';
      throw new Error(data.erro);
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

  async download(path, filename) {
    const headers = {};
    const token = this.getToken();
    if (token) headers.Authorization = `Bearer ${token}`;
    const res = await fetch(`${API_BASE}${path}`, { headers });

    if (res.status === 401) {
      this.clearSession();
      window.location.href = 'login.html';
      throw new Error('Não autenticado');
    }
    if (!res.ok) {
      const text = await res.text();
      let data = null;
      try {
        data = text ? JSON.parse(text) : null;
      } catch {
        data = null;
      }
      const err = new Error((data && data.erro) || 'Erro ao baixar o arquivo');
      err.status = res.status;
      err.data = data;
      throw err;
    }

    const url = URL.createObjectURL(await res.blob());
    const link = document.createElement('a');
    link.href = url;
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    link.remove();
    window.setTimeout(() => URL.revokeObjectURL(url), 1000);
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

// Escapa texto vindo do banco/usuário antes de inserir em innerHTML.
function esc(value) {
  return String(value == null ? '' : value)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#39;');
}

// Listas oficiais (tipos de problema, veículo, dias, UFs) definidas no backend (constantes.py).
let _opcoesCache = null;
async function carregarOpcoes() {
  if (!_opcoesCache) {
    _opcoesCache = await Api.get('/api/opcoes');
  }
  return _opcoesCache;
}

function optionsHtml(lista, selecionado, placeholder) {
  const inicio = placeholder != null ? `<option value="">${esc(placeholder)}</option>` : '';
  return inicio + lista.map(o =>
    `<option value="${esc(o.valor)}" ${String(selecionado) === String(o.valor) ? 'selected' : ''}>${esc(o.rotulo)}</option>`
  ).join('');
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
