function renderLayout(active) {
  const empresa = Api.getEmpresa() || { nome: 'Empresa' };
  const nome = (empresa.nome || 'Empresa').slice(0, 16);

  const nav = document.createElement('nav');
  nav.className = 'sidebar';
  nav.innerHTML = `
    <div class="sidebar-logo">
      <img src="img/logo-truck.svg" alt="FixTruck" class="logo-icon">
      <span class="logo-text">FIX<strong>TRUCK</strong></span>
    </div>
    <ul class="sidebar-nav">
      <li><a href="dashboard.html" class="nav-link ${active === 'dashboard' ? 'active' : ''}"><span class="nav-icon">⊞</span> Dashboard</a></li>
      <li><a href="ocorrencias.html" class="nav-link ${active === 'ocorrencias' ? 'active' : ''}"><span class="nav-icon">⚠</span> Ocorrências</a></li>
      <li><a href="orcamentos.html" class="nav-link ${active === 'orcamentos' ? 'active' : ''}"><span class="nav-icon">💵</span> Orçamentos</a></li>
      <li><a href="frota.html" class="nav-link ${active === 'frota' ? 'active' : ''}"><span class="nav-icon">🚚</span> Frota</a></li>
      <li><a href="oficinas.html" class="nav-link ${active === 'oficinas' ? 'active' : ''}"><span class="nav-icon">🔧</span> Oficinas</a></li>
      <li><a href="relatorios.html" class="nav-link ${active === 'relatorios' ? 'active' : ''}"><span class="nav-icon">📊</span> Relatórios</a></li>
    </ul>
    <div class="sidebar-footer">
      <a href="perfil.html" class="nav-link ${active === 'perfil' ? 'active' : ''}"><span class="nav-icon">👤</span> ${nome}</a>
      <a href="#" id="logout-link" class="nav-link logout-link"><span class="nav-icon">↩</span> Sair</a>
    </div>
  `;

  const main = document.createElement('main');
  main.className = 'main-content';
  [...document.body.childNodes].forEach((node) => {
    if (node.nodeType === 1 && node.tagName === 'SCRIPT') return;
    main.appendChild(node);
  });
  document.body.insertBefore(nav, document.body.firstChild);
  document.body.insertBefore(main, nav.nextSibling);

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
