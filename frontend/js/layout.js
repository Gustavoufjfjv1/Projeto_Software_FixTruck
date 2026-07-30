function renderLayout(active) {
  const empresa = Api.getEmpresa() || { nome: 'Empresa' };
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
      <li><a href="dashboard.html" class="nav-link ${active === 'dashboard' ? 'active' : ''}"><span class="nav-icon">${Icons.dashboard()}</span> <span class="nav-label">Dashboard</span></a></li>
      <li><a href="ocorrencias.html" class="nav-link ${active === 'ocorrencias' ? 'active' : ''}"><span class="nav-icon">${Icons.alert()}</span> <span class="nav-label">Ocorrências</span></a></li>
      <li><a href="orcamentos.html" class="nav-link ${active === 'orcamentos' ? 'active' : ''}"><span class="nav-icon">${Icons.wallet()}</span> <span class="nav-label">Orçamentos</span></a></li>
      <li><a href="frota.html" class="nav-link ${active === 'frota' ? 'active' : ''}"><span class="nav-icon">${Icons.truck()}</span> <span class="nav-label">Frota</span></a></li>
      <li><a href="oficinas.html" class="nav-link ${active === 'oficinas' ? 'active' : ''}"><span class="nav-icon">${Icons.wrench()}</span> <span class="nav-label">Oficinas</span></a></li>
      <li><a href="relatorios.html" class="nav-link ${active === 'relatorios' ? 'active' : ''}"><span class="nav-icon">${Icons.chart()}</span> <span class="nav-label">Relatórios</span></a></li>
    </ul>
    <div class="sidebar-footer">
      <a href="perfil.html" class="nav-link ${active === 'perfil' ? 'active' : ''}"><span class="nav-icon">${Icons.user()}</span> <span class="nav-label">${nome}</span></a>
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
    window.location.href = 'index.html';
  });
}

document.addEventListener('DOMContentLoaded', () => {
  document.querySelectorAll('.bar-fill').forEach((bar) => {
    const w = bar.style.width;
    bar.style.width = '0';
    setTimeout(() => { bar.style.width = w; }, 100);
  });
});
