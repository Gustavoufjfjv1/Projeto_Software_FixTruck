// Bloco "local da ocorrência" compartilhado (empresa e motorista):
// GPS do navegador -> endereço aproximado; endereço digitado -> coordenadas;
// se o GPS falhar (permissão negada, indisponível, tempo esgotado), o usuário informa o local manualmente.

const Localizacao = {
  html(valores = {}) {
    const v = (k) => esc(valores[k] || '');
    return `
      <div class="form-group">
        <label for="via">Rodovia / Avenida</label>
        <input type="text" id="via" maxlength="120" value="${v('via')}" placeholder="Ex: Rodovia Anhanguera ou Av. Brasil">
      </div>
      <div class="form-row">
        <div class="form-group">
          <label for="km">KM</label>
          <input type="text" id="km" inputmode="numeric" maxlength="10" value="${v('km')}" placeholder="Ex: 45">
        </div>
        <div class="form-group">
          <label for="cidade">Cidade</label>
          <input type="text" id="cidade" maxlength="80" value="${v('cidade')}" placeholder="Ex: Campinas/SP">
        </div>
      </div>
      <div id="enderecoStatus" style="font-size:12px;color:var(--gray-400);margin:-8px 0 16px"></div>

      <div class="form-group">
        <label>Localização atual (GPS)</label>
        <button type="button" class="location-btn" id="locBtn">Usar minha localização atual</button>
        <input type="hidden" id="lat" value="${v('lat')}">
        <input type="hidden" id="lon" value="${v('lon')}">
        <div id="locStatus" style="font-size:12px;color:var(--gray-400);margin-top:6px">
          ${valores.lat && valores.lon ? `Coordenadas registradas: ${v('lat')}, ${v('lon')}` : 'Opcional: capture as coordenadas para calcular a distância até as oficinas.'}
        </div>
      </div>

      <details id="coordsManuais" style="margin:-6px 0 16px">
        <summary style="cursor:pointer;font-size:13px;color:var(--gray-600)">GPS não funcionou? Informar coordenadas manualmente</summary>
        <div class="form-row" style="margin-top:10px">
          <div class="form-group">
            <label for="lat_manual">Latitude</label>
            <input type="number" id="lat_manual" step="any" min="-90" max="90" placeholder="-21.7609">
          </div>
          <div class="form-group">
            <label for="lon_manual">Longitude</label>
            <input type="number" id="lon_manual" step="any" min="-180" max="180" placeholder="-43.3500">
          </div>
        </div>
        <p style="font-size:12px;color:var(--gray-400)">Dica: no Google Maps, toque e segure no local para ver as coordenadas.</p>
      </details>`;
  },

  el(id) {
    return document.getElementById(id);
  },

  mensagemErroGps(err) {
    if (!err) return 'Seu navegador não oferece geolocalização.';
    if (err.code === 1) return 'Permissão de localização negada.';
    if (err.code === 2) return 'Localização indisponível no momento (sem sinal de GPS/rede).';
    if (err.code === 3) return 'O GPS demorou demais para responder.';
    return 'Não foi possível obter a localização.';
  },

  falhaGps(err) {
    const status = this.el('locStatus');
    status.textContent = `${this.mensagemErroGps(err)} Informe a rodovia/avenida e a cidade abaixo `
      + '(ou as coordenadas manualmente) para continuar.';
    status.style.color = 'var(--red)';
    this.el('locBtn').textContent = 'Tentar GPS novamente';
    this.el('locBtn').disabled = false;
    this.el('coordsManuais').open = true;
    this.el('via').focus();
  },

  async preencherEnderecoPorGps(lat, lon) {
    const resultado = await Geo.enderecoPorCoordenadas(lat, lon);
    if (!resultado) return false;
    if (resultado.via && !this.el('via').value) this.el('via').value = resultado.via;
    if (resultado.cidade && !this.el('cidade').value) this.el('cidade').value = resultado.cidade;
    return Boolean(resultado.via || resultado.cidade);
  },

  capturarGps() {
    const btn = this.el('locBtn');
    const status = this.el('locStatus');
    if (!navigator.geolocation) {
      this.falhaGps(null);
      return;
    }
    btn.disabled = true;
    btn.textContent = 'Obtendo localização...';
    navigator.geolocation.getCurrentPosition(async (pos) => {
      const lat = pos.coords.latitude;
      const lon = pos.coords.longitude;
      this.el('lat').value = lat;
      this.el('lon').value = lon;
      btn.textContent = 'Localização capturada ✓';
      btn.disabled = false;
      status.style.color = 'var(--green-dark)';
      status.textContent = `Localização capturada: ${lat.toFixed(5)}, ${lon.toFixed(5)}. Buscando endereço...`;
      const preencheu = await this.preencherEnderecoPorGps(lat, lon);
      status.textContent = preencheu
        ? `Localização capturada: ${lat.toFixed(5)}, ${lon.toFixed(5)} — endereço preenchido automaticamente, confira.`
        : `Localização capturada: ${lat.toFixed(5)}, ${lon.toFixed(5)}. Endereço não identificado — preencha se quiser.`;
    }, (err) => this.falhaGps(err), { enableHighAccuracy: true, timeout: 12000, maximumAge: 60000 });
  },

  // Endereço digitado sem GPS: busca coordenadas para a busca por distância continuar funcionando.
  async geocodificarEndereco() {
    if (this.el('lat').value && this.el('lon').value) return;
    const via = this.el('via').value.trim();
    const cidade = this.el('cidade').value.trim();
    if (!via && !cidade) return;
    const st = this.el('enderecoStatus');
    st.textContent = 'Localizando endereço...';
    const coords = await Geo.coordenadasPorEndereco(via, cidade);
    if (coords) {
      this.el('lat').value = coords.lat;
      this.el('lon').value = coords.lon;
      st.textContent = 'Endereço localizado — a busca de oficinas poderá calcular distâncias.';
      st.style.color = 'var(--green-dark)';
    } else {
      st.textContent = 'Endereço não localizado automaticamente. A ocorrência pode ser registrada, '
        + 'mas sem distância até as oficinas (informe as coordenadas manualmente, se souber).';
      st.style.color = 'var(--gray-400)';
    }
  },

  aplicarCoordenadasManuais() {
    const lat = this.el('lat_manual').value;
    const lon = this.el('lon_manual').value;
    if (lat === '' && lon === '') return null;
    const la = Number(lat);
    const lo = Number(lon);
    if (lat === '' || lon === '' || !Number.isFinite(la) || !Number.isFinite(lo) || la < -90 || la > 90 || lo < -180 || lo > 180) {
      return 'Coordenadas manuais inválidas: latitude entre -90 e 90 e longitude entre -180 e 180.';
    }
    this.el('lat').value = la;
    this.el('lon').value = lo;
    return null;
  },

  ligar() {
    this.el('locBtn').addEventListener('click', () => this.capturarGps());
    this.el('via').addEventListener('blur', () => this.geocodificarEndereco());
    this.el('cidade').addEventListener('blur', () => this.geocodificarEndereco());
  },

  // Retorna { erro } ou { dados } com via, km, cidade, endereco, lat, lon.
  async coletar() {
    const erroManual = this.aplicarCoordenadasManuais();
    if (erroManual) return { erro: erroManual };
    await this.geocodificarEndereco();
    const via = this.el('via').value.trim();
    const km = this.el('km').value.trim();
    const cidade = this.el('cidade').value.trim();
    const lat = this.el('lat').value;
    const lon = this.el('lon').value;
    const endereco = [via, km ? `KM ${km}` : '', cidade].filter(Boolean).join(' — ');
    const temGps = Boolean(lat && lon);
    if (!temGps && (!via || !cidade)) {
      return { erro: 'Informe a rodovia/avenida e a cidade, ou capture o GPS.' };
    }
    return { dados: { via, km, cidade, endereco, lat: lat || null, lon: lon || null } };
  },

  // "Rodovia — KM 45 — Cidade/UF" -> partes (para edição).
  separarEndereco(endereco) {
    if (!endereco || endereco.startsWith('GPS:')) return { via: '', km: '', cidade: '' };
    const partes = endereco.split(' — ').map(p => p.trim());
    const resto = partes.slice(1);
    if (resto[0] && resto[0].toUpperCase().startsWith('KM ')) {
      return { via: partes[0] || '', km: resto[0].slice(3).trim(), cidade: resto[1] || '' };
    }
    return { via: partes[0] || '', km: '', cidade: resto[0] || '' };
  },
};
