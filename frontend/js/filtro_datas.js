// Filtro de período compartilhado (ocorrências e relatórios): atalhos 7/30/90 dias
// ou intervalo personalizado (data_inicio/data_fim, dia final incluído). Lê e grava na URL.

const FiltroDatas = {
  html() {
    return `
      <select id="filtro_periodo" class="filter-select" aria-label="Período">
        <option value="">Todo período</option>
        <option value="7d">Últimos 7 dias</option>
        <option value="30d">Últimos 30 dias</option>
        <option value="90d">Últimos 90 dias</option>
        <option value="intervalo">Intervalo de datas…</option>
      </select>
      <span id="intervalo-datas" style="display:none;align-items:center;gap:6px;flex-wrap:wrap">
        <label for="data_inicio" style="font-size:13px;color:var(--gray-600)">De</label>
        <input type="date" id="data_inicio" class="filter-select">
        <label for="data_fim" style="font-size:13px;color:var(--gray-600)">até</label>
        <input type="date" id="data_fim" class="filter-select">
        <button type="button" id="aplicar-datas" class="btn btn-primary btn-sm">Aplicar</button>
      </span>
      <span id="erro-datas" role="alert" style="color:var(--red);font-size:13px"></span>`;
  },

  atuais() {
    return { periodo: qs('periodo') || '', data_inicio: qs('data_inicio') || '', data_fim: qs('data_fim') || '' };
  },

  ativo() {
    const a = this.atuais();
    return Boolean(a.periodo || a.data_inicio || a.data_fim);
  },

  mostrarIntervalo(sim) {
    document.getElementById('intervalo-datas').style.display = sim ? 'inline-flex' : 'none';
  },

  // Devolve {periodo} | {data_inicio, data_fim} ou null se o intervalo for inválido.
  valores() {
    const sel = document.getElementById('filtro_periodo').value;
    if (sel !== 'intervalo') return sel ? { periodo: sel } : {};
    const inicio = document.getElementById('data_inicio').value;
    const fim = document.getElementById('data_fim').value;
    const erro = document.getElementById('erro-datas');
    erro.textContent = '';
    if (!inicio && !fim) {
      erro.textContent = 'Informe ao menos uma das datas.';
      return null;
    }
    if (inicio && fim && inicio > fim) {
      erro.textContent = 'A data inicial deve ser anterior ou igual à data final.';
      return null;
    }
    const v = {};
    if (inicio) v.data_inicio = inicio;
    if (fim) v.data_fim = fim;
    return v;
  },

  // onMudar(valores) é chamado ao escolher um atalho ou ao aplicar um intervalo válido.
  ligar(onMudar) {
    const a = this.atuais();
    const sel = document.getElementById('filtro_periodo');
    if (a.data_inicio || a.data_fim) {
      sel.value = 'intervalo';
      document.getElementById('data_inicio').value = a.data_inicio;
      document.getElementById('data_fim').value = a.data_fim;
      this.mostrarIntervalo(true);
    } else {
      sel.value = a.periodo;
    }
    sel.addEventListener('change', () => {
      if (sel.value === 'intervalo') {
        this.mostrarIntervalo(true);
        document.getElementById('data_inicio').focus();
        return;
      }
      this.mostrarIntervalo(false);
      onMudar(this.valores());
    });
    document.getElementById('aplicar-datas').addEventListener('click', () => {
      const v = this.valores();
      if (v) onMudar(v);
    });
  },
};
