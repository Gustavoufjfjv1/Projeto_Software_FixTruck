function navEmpresa(active) {
  const item = (pagina, chave, icone, rotulo) =>
    `<li><a href="${pagina}" class="nav-link ${active === chave ? 'active' : ''}"><span class="nav-icon">${icone}</span> <span class="nav-label">${rotulo}</span></a></li>`;
  return [
    item('dashboard.html', 'dashboard', Icons.dashboard(), 'Dashboard'),
    item('ocorrencias.html', 'ocorrencias', Icons.alert(), 'Ocorrências'),
    item('frota.html', 'frota', Icons.truck(), 'Frota'),
    item('oficinas.html', 'oficinas', Icons.star(20, true), 'Favoritas'),
    item('gerenciar_oficinas.html', 'gerenciar_oficinas', Icons.wrench(20), 'Cadastro de oficinas'),
    item('relatorios.html', 'relatorios', Icons.chart(), 'Relatórios'),
  ].join('');
}

function navMotorista(active) {
  const item = (pagina, chave, icone, rotulo) =>
    `<li><a href="${pagina}" class="nav-link ${active === chave ? 'active' : ''}"><span class="nav-icon">${icone}</span> <span class="nav-label">${rotulo}</span></a></li>`;
  return [
    item('motorista_painel.html', 'painel', Icons.clipboard(20), 'Minhas ocorrências'),
    item('motorista_nova_ocorrencia.html', 'nova', Icons.alert(), 'Registrar ocorrência'),
  ].join('');
}

function renderLayout(active) {
  const motorista = Api.papel() === 'motorista';
  const empresa = motorista
    ? { nome: (Api.getMotorista() || {}).nome || 'Motorista' }
    : (Api.getEmpresa() || { nome: 'Empresa' });
  const nome = (empresa.nome || 'Empresa').slice(0, 16);

  document.body.classList.add('app-shell');

  const overlay = document.createElement('div');
  overlay.className = 'sidebar-overlay';
  overlay.id = 'sidebar-overlay';

  const toggle = document.createElement('button');
  toggle.type = 'button';
  toggle.className = 'menu-toggle';
  toggle.id = 'menu-toggle';
  toggle.setAttribute('aria-label', 'Abrir menu');
  toggle.innerHTML = `
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true">
      <line x1="3" y1="6" x2="21" y2="6"/><line x1="3" y1="12" x2="21" y2="12"/><line x1="3" y1="18" x2="21" y2="18"/>
    </svg>
  `;

  const nav = document.createElement('nav');
  nav.className = 'sidebar';
  nav.id = 'app-sidebar';
  nav.innerHTML = `
    <div class="sidebar-logo">
      <img src="img/logo-truck.svg" alt="FixTruck" class="logo-icon">
      <span class="logo-text">FIX<strong>TRUCK</strong></span>
      <button type="button" class="sidebar-close" id="sidebar-close" aria-label="Fechar menu">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true">
          <line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/>
        </svg>
      </button>
    </div>
    <ul class="sidebar-nav">
      ${motorista ? navMotorista(active) : navEmpresa(active)}
    </ul>
    <div class="sidebar-footer">
      ${motorista
        ? `<span class="nav-link"><span class="nav-icon">${Icons.user()}</span> <span class="nav-label">${esc(nome)} (motorista)</span></span>`
        : `<a href="perfil.html" class="nav-link ${active === 'perfil' ? 'active' : ''}"><span class="nav-icon">${Icons.user()}</span> <span class="nav-label">${esc(nome)}</span></a>`}
      <a href="#" id="logout-link" class="nav-link logout-link"><span class="nav-icon">${Icons.logout()}</span> <span class="nav-label">Sair</span></a>
    </div>
  `;

  const main = document.createElement('main');
  main.className = 'main-content';
  [...document.body.childNodes].forEach((node) => {
    if (node.nodeType === 1 && node.tagName === 'SCRIPT') return;
    main.appendChild(node);
  });

  document.body.insertBefore(overlay, document.body.firstChild);
  document.body.insertBefore(toggle, document.body.firstChild);
  document.body.insertBefore(nav, document.body.firstChild);
  document.body.insertBefore(main, nav.nextSibling);

  const openMenu = () => document.body.classList.add('sidebar-open');
  const closeMenu = () => document.body.classList.remove('sidebar-open');

  toggle.addEventListener('click', openMenu);
  overlay.addEventListener('click', closeMenu);
  document.getElementById('sidebar-close').addEventListener('click', closeMenu);
  window.addEventListener('resize', () => {
    if (window.innerWidth > 900) closeMenu();
  });

  document.getElementById('logout-link').addEventListener('click', (e) => {
    e.preventDefault();
    Api.clearSession();
    window.location.href = motorista ? 'motorista_login.html' : 'index.html';
  });
}

document.addEventListener('DOMContentLoaded', () => {
  document.querySelectorAll('.bar-fill').forEach((bar) => {
    const w = bar.style.width;
    bar.style.width = '0';
    setTimeout(() => { bar.style.width = w; }, 100);
  });
});
