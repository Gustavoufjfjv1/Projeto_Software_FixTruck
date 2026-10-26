// Renderização compartilhada da busca de oficinas compatíveis (empresa e motorista).
// A API já devolve somente oficinas compatíveis em `oficinas`; incompatíveis vêm à parte em `alternativas`.

const BuscaOficinas = {
  tags(especialidades, tipoProblema) {
    return (especialidades || '').split(',').map(esp => {
      const t = esp.trim();
      if (!t) return '';
      const destaque = tipoProblema && t.toLowerCase() === String(tipoProblema).toLowerCase();
      return `<span class="oficina-tag" style="${destaque ? 'background:var(--green);color:white' : ''}">${esc(t)}</span>`;
    }).join('');
  },

  selos(of) {
    const selos = [];
    if (of.compativel) selos.push(`<span class="badge badge-green">${Icons.checkSimple(12)} Compatível</span>`);
    if (of.tem_guincho) selos.push('<span class="guincho-badge">Guincho</span>');
    if (of.aberta_24h) selos.push('<span class="badge badge-blue">24h</span>');
    if (of.aberta_agora) selos.push('<span class="badge badge-green">● Aberta agora</span>');
    else if (of.abre_em_minutos) selos.push(`<span class="badge badge-orange">Abre em ${of.abre_em_minutos} min</span>`);
    else selos.push('<span class="badge badge-gray">● Fechada agora</span>');
    if (of.favoritada) selos.push(`<span class="badge badge-orange">${Icons.star(12, true)} Favorita</span>`);
    return `<div style="display:flex;gap:6px;flex-wrap:wrap;margin:8px 0">${selos.join('')}</div>`;
  },

  card(of, oc, opts, alternativa) {
    const motivos = alternativa
      ? `<div class="alert alert-texto alert-warning" style="margin:10px 0 0;padding:8px 12px;font-size:12px">
           <strong>Não compatível:</strong> ${(of.motivos_incompatibilidade || []).map(esc).join(' · ')}
         </div>`
      : '';
    const acoes = [];
    if (opts.podeSelecionar && !alternativa) {
      acoes.push(`<button type="button" class="btn btn-primary btn-sm" data-vincular="${of.id}" data-aberta="${of.aberta_agora ? '1' : '0'}">Selecionar oficina</button>`);
    }
    if (of.telefone) acoes.push(`<a href="tel:${esc(of.telefone)}" class="btn btn-outline btn-sm">${Icons.phone(14)} Ligar</a>`);
    if (opts.linkDetalhe) acoes.push(`<a href="detalhe_oficina.html?id=${of.id}" class="btn btn-outline btn-sm">Ver detalhes</a>`);
    if (opts.podeFavoritar) {
      acoes.push(`<button type="button" class="fav-btn ${of.favoritada ? 'active' : ''}" data-fav="${of.id}" title="Favoritar" style="margin-left:auto">
        ${of.favoritada ? Icons.star(18, true) : Icons.star(18, false)}</button>`);
    }
    return `
    <div class="oficina-card ${alternativa ? 'oficina-card-alternativa' : 'oficina-card-recomendada'}">
        <div class="oficina-card-header">
            <div>
                <div class="oficina-name">${esc(of.nome)}</div>
                <div class="oficina-sub">${esc(of.endereco || '')}${of.cidade ? ' — ' + esc(of.cidade) + '/' + esc(of.uf || '') : ''}</div>
            </div>
        </div>
        ${alternativa ? '' : this.selos(of)}
        <div class="oficina-tags">${this.tags(of.especialidades, oc.tipo_problema)}</div>
        <div class="oficina-meta">
            ${of.distancia != null ? `<span><strong>${of.distancia} km</strong></span>` : ''}
            <span>Veículos: ${esc(of.tipos_veiculo || '')}</span>
        </div>
        <div style="margin-top:8px;font-size:12px;color:var(--gray-600)">
            Horário: ${esc(of.horario_resumo || '')}${of.telefone ? ` &nbsp;|&nbsp; ${esc(of.telefone)}` : ''}
        </div>
        ${motivos}
        <div style="display:flex;gap:10px;margin-top:14px;align-items:center;flex-wrap:wrap">${acoes.join('')}</div>
    </div>`;
  },

  mapa(oc, oficinas) {
    const container = document.getElementById('mapa-busca');
    if (!container || typeof L === 'undefined') return;
    const map = L.map('mapa-busca', { scrollWheelZoom: false });
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
      attribution: '&copy; colaboradores do OpenStreetMap',
      maxZoom: 18,
    }).addTo(map);
    const bounds = [];
    if (oc.lat && oc.lon) {
      const truckIcon = L.divIcon({ className: 'map-marker-icon map-marker-truck', html: '🚚', iconSize: [30, 30] });
      L.marker([Number(oc.lat), Number(oc.lon)], { icon: truckIcon }).addTo(map)
        .bindPopup('<strong>Local da ocorrência</strong>');
      bounds.push([Number(oc.lat), Number(oc.lon)]);
    }
    oficinas.forEach(of => {
      if (of.lat == null || of.lon == null) return;
      const cor = of.tem_guincho ? '#00a854' : '#2563eb';
      const icon = L.divIcon({ className: 'map-marker-icon', html: `<div style="background:${cor}">🔧</div>`, iconSize: [28, 28] });
      const popup = `<strong>${esc(of.nome)}</strong><br>
        ${of.distancia != null ? of.distancia + ' km &middot; ' : ''}${of.aberta_agora ? 'Aberta agora' : (of.abre_em_minutos ? 'Abre em ' + of.abre_em_minutos + ' min' : 'Fechada')}
        ${of.tem_guincho ? '<br>🛻 Guincho disponível' : ''}`;
      L.marker([Number(of.lat), Number(of.lon)], { icon }).addTo(map).bindPopup(popup);
      bounds.push([Number(of.lat), Number(of.lon)]);
    });
    const centro = oc.lat && oc.lon ? [Number(oc.lat), Number(oc.lon)] : null;
    const proximos = centro
      ? bounds.filter(([la, lo]) => (la - centro[0]) ** 2 + (lo - centro[1]) ** 2 < 0.35 ** 2)
      : bounds;
    if (proximos.length > 1) map.fitBounds(proximos, { padding: [30, 30], maxZoom: 14 });
    else if (centro) map.setView(centro, 14);
    else if (bounds.length) map.fitBounds(bounds, { padding: [30, 30], maxZoom: 13 });
  },

  filtros(data, opts) {
    const raio = data.raio != null ? String(Math.trunc(Number(data.raio))) : '';
    const janela = String(data.janela_minutos || 0);
    const opRaio = ['', '5', '10', '20', '50', '100', '200', '500'].map(v =>
      `<option value="${v}" ${v === raio ? 'selected' : ''}>${v ? 'Até ' + v + ' km' : 'Sem limite'}</option>`).join('');
    const opJanela = [['0', 'Aberta agora'], ['60', 'Abre em até 1 h'], ['120', 'Abre em até 2 h'], ['480', 'Abre em até 8 h']]
      .map(([v, r]) => `<option value="${v}" ${v === janela ? 'selected' : ''}>${r}</option>`).join('');
    return `
      <div class="card" style="margin-bottom:20px;padding:16px 20px">
        <div class="filters-bar" style="margin-bottom:0">
          <label style="font-size:13px;font-weight:600;color:var(--gray-700)" for="raio">Raio</label>
          <select id="raio" class="filter-select" ${data.sem_localizacao ? 'disabled title="Ocorrência sem localização"' : ''}>${opRaio}</select>
          <label style="font-size:13px;font-weight:600;color:var(--gray-700)" for="janela">Horário</label>
          <select id="janela" class="filter-select">${opJanela}</select>
          <span style="font-size:13px;color:var(--gray-400)">${data.oficinas.length} oficina(s) compatível(is) de ${data.total_avaliadas} ativas</span>
        </div>
      </div>`;
  },

  render(root, data, opts) {
    const oc = data.ocorrencia;
    const oficinas = data.oficinas || [];
    const alternativas = data.alternativas || [];
    const temMapa = oficinas.some(of => of.lat != null && of.lon != null);

    const lista = oficinas.length
      ? `<div class="oficinas-grid">${oficinas.map(of => this.card(of, oc, opts, false)).join('')}</div>`
      : `<div class="card" style="border:2px solid var(--red)">
           <div class="empty-state" style="padding:24px">
             <div class="empty-icon">${Icons.wrench(48)}</div>
             <h3>Nenhuma oficina compatível encontrada</h3>
             <p>${esc(data.detalhe || data.mensagem || '')}</p>
             <p style="font-size:13px;color:var(--gray-500)">Tente aumentar o raio ou a janela de horário.</p>
           </div>
         </div>
         ${alternativas.length ? `
         <h2 style="margin:28px 0 6px;font-size:18px">Alternativas parciais — NÃO compatíveis</h2>
         <p style="font-size:13px;color:var(--gray-500);margin-bottom:12px">
           Estas oficinas não atendem a todos os critérios da ocorrência. Confirme por telefone antes de acionar.
         </p>
         <div class="oficinas-grid">${alternativas.map(of => this.card(of, oc, opts, true)).join('')}</div>` : ''}`;

    root.innerHTML = `
      <div class="page-header">
        <div>
          <h1>Oficinas compatíveis</h1>
          <p>Ocorrência #${oc.id} — veículo ${esc(oc.tipo_veiculo || '')} / problema ${esc(oc.tipo_problema || '')}
             ${oc.pane_total ? '<span class="badge badge-red" style="margin-left:8px">PANE TOTAL</span>' : ''}</p>
        </div>
        <a href="${opts.voltarHref}" class="btn btn-outline">${Icons.arrowLeft(16)} ${esc(opts.voltarTexto || 'Voltar')}</a>
      </div>
      <div class="alert alert-texto alert-info">
        Só aparecem na lista principal oficinas <strong>ativas</strong>, que atendem o <strong>problema</strong> e o
        <strong>veículo</strong>${oc.pane_total ? ', possuem <strong>guincho</strong> (pane total)' : ''},
        estão <strong>abertas</strong> (fuso de Brasília) e dentro do <strong>raio</strong>. Ordem: menor distância.
      </div>
      ${data.sem_localizacao ? `<div class="alert alert-texto alert-warning">
        Ocorrência sem localização — não é possível calcular distância nem filtrar por raio.
        Edite a ocorrência e informe o endereço ou o GPS.</div>` : ''}
      ${this.filtros(data, opts)}
      ${temMapa ? '<div id="mapa-busca" class="map-busca-container"></div>' : ''}
      ${lista}
      ${opts.rodape || ''}`;

    const atualizar = () => {
      const r = document.getElementById('raio').value;
      const j = document.getElementById('janela').value;
      opts.onFiltro({ raio: r, janela: j });
    };
    document.getElementById('raio').addEventListener('change', atualizar);
    document.getElementById('janela').addEventListener('change', atualizar);
    if (temMapa) this.mapa(oc, oficinas);
    root.querySelectorAll('[data-vincular]').forEach(btn => btn.addEventListener('click', () => {
      if (btn.dataset.aberta === '0' &&
          !window.confirm('Esta oficina ainda não está aberta (abre dentro da janela escolhida). Deseja selecioná-la mesmo assim?')) {
        return;
      }
      opts.onVincular(btn.dataset.vincular);
    }));
    root.querySelectorAll('[data-fav]').forEach(btn => btn.addEventListener('click', () => opts.onFavoritar(btn.dataset.fav)));
    if (typeof hydrateIcons === 'function') hydrateIcons(root);
  },
};
