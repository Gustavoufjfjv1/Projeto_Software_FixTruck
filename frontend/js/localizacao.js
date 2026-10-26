// Bloco "local da ocorrência" compartilhado (empresa e motorista):
// GPS do navegador -> endereço aproximado; endereço digitado -> coordenadas;
// se o GPS falhar (permissão negada, indisponível, tempo esgotado), o usuário informa o local manualmente.

const Localizacao = {
  gpsSeq: 0,
  geoSeq: 0,
  pontoSeq: 0,
  origem: '',
  preenchendo: false,
  watchId: null,
  mapa: null,
  marcador: null,
  _montandoMapa: false,
  _pendenteMapa: null,
  _leaflet: null,

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
        <div id="mapa-local" class="map-busca-container" style="display:none;margin-top:10px"></div>
        <p id="mapa-dica" style="display:none;font-size:12px;color:var(--gray-500);margin:6px 0 0">
          O pino é a posição que o navegador informou. Se não for o local do veículo, arraste o pino até o ponto certo.
        </p>
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
    status.textContent = `${this.mensagemErroGps(err)} Informe a rodovia/avenida e a cidade `
      + '(ou as coordenadas manualmente) para continuar.';
    status.style.color = 'var(--red)';
    this.el('locBtn').textContent = 'Tentar GPS novamente';
    this.el('locBtn').disabled = false;
    this.el('coordsManuais').open = true;
    this.el('via').focus();
  },

  pararGps() {
    if (this.watchId != null && navigator.geolocation) {
      navigator.geolocation.clearWatch(this.watchId);
      this.watchId = null;
    }
  },

  garantirLeaflet() {
    if (window.L) return Promise.resolve();
    if (this._leaflet) return this._leaflet;
    this._leaflet = new Promise((resolve, reject) => {
      const css = document.createElement('link');
      css.rel = 'stylesheet';
      css.href = 'https://unpkg.com/leaflet@1.9.4/dist/leaflet.css';
      document.head.appendChild(css);
      const script = document.createElement('script');
      script.src = 'https://unpkg.com/leaflet@1.9.4/dist/leaflet.js';
      script.onload = () => resolve();
      script.onerror = () => reject(new Error('mapa'));
      document.head.appendChild(script);
    });
    return this._leaflet;
  },

  async mostrarMapa(lat, lon) {
    const el = this.el('mapa-local');
    const dica = this.el('mapa-dica');
    if (!el) return;
    el.style.display = '';
    if (dica) dica.style.display = '';
    this._pendenteMapa = [Number(lat), Number(lon)];
    if (this._montandoMapa) return;
    this._montandoMapa = true;
    try {
      await this.garantirLeaflet();
      while (this._pendenteMapa && this.el('mapa-local')) {
        const ll = this._pendenteMapa;
        this._pendenteMapa = null;
        const container = this.el('mapa-local');
        if (!this.mapa || this.mapa.getContainer() !== container) {
          this.mapa = L.map(container, { scrollWheelZoom: false }).setView(ll, 16);
          L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
            attribution: '&copy; colaboradores do OpenStreetMap',
            maxZoom: 19,
          }).addTo(this.mapa);
          const icon = L.divIcon({
            className: 'map-marker-truck',
            html: '📍',
            iconSize: [28, 28],
            iconAnchor: [14, 28],
          });
          this.marcador = L.marker(ll, { draggable: true, icon }).addTo(this.mapa);
          this.marcador.on('dragstart', () => this.pararGps());
          this.marcador.on('dragend', () => {
            const p = this.marcador.getLatLng();
            this.aplicarPonto(p.lat, p.lng, true);
          });
        } else {
          this.marcador.setLatLng(ll);
          this.mapa.setView(ll, Math.max(this.mapa.getZoom(), 16));
        }
        setTimeout(() => { if (this.mapa) this.mapa.invalidateSize(); }, 60);
      }
    } catch (e) {
      this._pendenteMapa = null;
      if (dica) dica.textContent = 'Não foi possível abrir o mapa. As coordenadas continuam valendo.';
    } finally {
      this._montandoMapa = false;
      if (this._pendenteMapa) {
        const [la, lo] = this._pendenteMapa;
        this.mostrarMapa(la, lo);
      }
    }
  },

  aplicarPonto(lat, lon, veioDoMapa) {
    const pontoSeq = ++this.pontoSeq;
    if (veioDoMapa) this.gpsSeq += 1;
    this.origem = 'gps';
    this.el('lat').value = lat;
    this.el('lon').value = lon;
    const status = this.el('locStatus');
    status.style.color = 'var(--green-dark)';
    status.textContent = veioDoMapa
      ? `Pino ajustado para ${Number(lat).toFixed(5)}, ${Number(lon).toFixed(5)}. Atualizando o endereço...`
      : status.textContent;
    this.preencherEnderecoPorGps(lat, lon, this.gpsSeq, pontoSeq).then((preencheu) => {
      if (pontoSeq !== this.pontoSeq) return;
      if (!veioDoMapa) return;
      status.textContent = preencheu
        ? `Pino ajustado: ${Number(lat).toFixed(5)}, ${Number(lon).toFixed(5)}. O endereço acompanhou esse ponto.`
        : `Pino ajustado: ${Number(lat).toFixed(5)}, ${Number(lon).toFixed(5)}. Complete o endereço se quiser.`;
    });
  },

  async preencherEnderecoPorGps(lat, lon, gpsSeq, pontoSeq) {
    const resultado = await Geo.enderecoPorCoordenadas(lat, lon);
    if (gpsSeq !== this.gpsSeq || (pontoSeq != null && pontoSeq !== this.pontoSeq)) return false;
    if (!resultado || !(resultado.via || resultado.cidade)) return false;
    // Substitui o que estava digitado: o texto precisa ser o do ponto do GPS, não de outro lugar.
    this.preenchendo = true;
    this.el('via').value = resultado.via || '';
    this.el('km').value = '';
    this.el('cidade').value = resultado.cidade || '';
    this.preenchendo = false;
    return true;
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
    this.pararGps();
    // maximumAge 0: não reutiliza posição antiga. watchPosition troca a leitura se surgir uma mais precisa.
    const gpsSeq = ++this.gpsSeq;
    this.geoSeq += 1;
    let melhor = Infinity;
    let recebeu = false;
    const opcoes = { enableHighAccuracy: true, timeout: 20000, maximumAge: 0 };
    const aplicar = async (pos) => {
      if (gpsSeq !== this.gpsSeq) return;
      const precisao = Number(pos.coords.accuracy);
      if (Number.isFinite(precisao) && precisao >= melhor) return;
      if (Number.isFinite(precisao)) melhor = precisao;
      recebeu = true;
      const lat = pos.coords.latitude;
      const lon = pos.coords.longitude;
      const pontoSeq = ++this.pontoSeq;
      this.origem = 'gps';
      this.el('lat').value = lat;
      this.el('lon').value = lon;
      btn.textContent = 'Localização capturada ✓';
      btn.disabled = false;
      status.style.color = 'var(--green-dark)';
      status.textContent = `Posição atual: ${lat.toFixed(5)}, ${lon.toFixed(5)}. Buscando o endereço desse ponto...`;
      this.mostrarMapa(lat, lon);
      const preencheu = await this.preencherEnderecoPorGps(lat, lon, gpsSeq, pontoSeq);
      if (gpsSeq !== this.gpsSeq || pontoSeq !== this.pontoSeq) return;
      const avisoPrecisao = Number.isFinite(precisao) && precisao > 1000
        ? ` O navegador indicou precisão de cerca de ${Math.round(precisao)} m (localização de rede, não um GPS fino). No celular, permita a localização precisa.`
        : (Number.isFinite(precisao) ? ` Precisão de cerca de ${Math.round(precisao)} m.` : '');
      status.textContent = preencheu
        ? `Posição atual capturada: ${lat.toFixed(5)}, ${lon.toFixed(5)}.${avisoPrecisao} Confira o pino no mapa e arraste se não for o veículo.`
        : `Posição atual capturada: ${lat.toFixed(5)}, ${lon.toFixed(5)}.${avisoPrecisao} Confira o pino no mapa.`;
      if (Number.isFinite(precisao) && precisao <= 40) this.pararGps();
    };
    this.watchId = navigator.geolocation.watchPosition(aplicar, (err) => {
      if (gpsSeq !== this.gpsSeq || recebeu) return;
      this.falhaGps(err);
      this.pararGps();
    }, opcoes);
    window.setTimeout(() => {
      if (gpsSeq === this.gpsSeq) this.pararGps();
    }, 12000);
  },

  // Endereço digitado sem GPS: busca coordenadas para a busca por distância continuar funcionando.
  async geocodificarEndereco() {
    if (this.origem === 'gps' && this.el('lat').value && this.el('lon').value) return;
    const via = this.el('via').value.trim();
    const cidade = this.el('cidade').value.trim();
    if (!via && !cidade) return;
    const geoSeq = ++this.geoSeq;
    const st = this.el('enderecoStatus');
    st.textContent = 'Localizando endereço...';
    const coords = await Geo.coordenadasPorEndereco(via, cidade);
    if (geoSeq !== this.geoSeq || this.origem === 'gps') return;
    if (coords) {
      this.origem = 'endereco';
      this.el('lat').value = coords.lat;
      this.el('lon').value = coords.lon;
      this.mostrarMapa(coords.lat, coords.lon);
      st.textContent = 'Endereço localizado — confira o pino no mapa. A busca de oficinas usa esse ponto.';
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
    this.origem = 'manual';
    this.gpsSeq += 1;
    this.geoSeq += 1;
    this.el('lat').value = la;
    this.el('lon').value = lo;
    return null;
  },

  descartarGpsSeEditar() {
    if (this.preenchendo || this.origem !== 'gps') return;
    this.origem = '';
    this.el('lat').value = '';
    this.el('lon').value = '';
    this.gpsSeq += 1;
    this.geoSeq += 1;
    const status = this.el('locStatus');
    status.style.color = 'var(--gray-400)';
    status.textContent = 'O endereço foi alterado e as coordenadas do GPS foram descartadas. Capture a localização de novo ou deixe o sistema localizar o endereço digitado.';
  },

  ligar() {
    if (this.mapa && (!this.el('mapa-local') || this.mapa.getContainer() !== this.el('mapa-local'))) {
      this.mapa = null;
      this.marcador = null;
    }
    const lat = this.el('lat').value;
    const lon = this.el('lon').value;
    if (lat && lon) {
      this.origem = 'gps';
      this.mostrarMapa(lat, lon);
    }
    this.el('locBtn').addEventListener('click', () => this.capturarGps());
    ['via', 'km', 'cidade'].forEach(id => {
      this.el(id).addEventListener('input', () => this.descartarGpsSeEditar());
    });
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
