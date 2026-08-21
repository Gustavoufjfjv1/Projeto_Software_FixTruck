const UF_POR_ESTADO = {
  'Acre': 'AC', 'Alagoas': 'AL', 'Amapá': 'AP', 'Amazonas': 'AM', 'Bahia': 'BA',
  'Ceará': 'CE', 'Distrito Federal': 'DF', 'Espírito Santo': 'ES', 'Goiás': 'GO',
  'Maranhão': 'MA', 'Mato Grosso': 'MT', 'Mato Grosso do Sul': 'MS', 'Minas Gerais': 'MG',
  'Pará': 'PA', 'Paraíba': 'PB', 'Paraná': 'PR', 'Pernambuco': 'PE', 'Piauí': 'PI',
  'Rio de Janeiro': 'RJ', 'Rio Grande do Norte': 'RN', 'Rio Grande do Sul': 'RS',
  'Rondônia': 'RO', 'Roraima': 'RR', 'Santa Catarina': 'SC', 'São Paulo': 'SP',
  'Sergipe': 'SE', 'Tocantins': 'TO',
};

// Geocodificação via OpenStreetMap/Nominatim (gratuito, sem chave de API).
const Geo = {
  // GPS -> endereço aproximado (usado ao capturar localização atual).
  async enderecoPorCoordenadas(lat, lon) {
    try {
      const resp = await fetch(
        `https://nominatim.openstreetmap.org/reverse?format=jsonv2&lat=${lat}&lon=${lon}&zoom=16&addressdetails=1`
      );
      if (!resp.ok) return null;
      const data = await resp.json();
      const addr = data.address || {};
      const via = addr.road || addr.pedestrian || addr.residential || '';
      const cidadeBase = addr.city || addr.town || addr.village || addr.municipality || '';
      const uf = addr.state ? (UF_POR_ESTADO[addr.state] || addr.state) : '';
      const cidade = cidadeBase ? (uf ? `${cidadeBase}/${uf}` : cidadeBase) : '';
      if (!via && !cidade) return null;
      return { via, cidade };
    } catch (e) {
      return null;
    }
  },

  // Endereço digitado -> coordenadas (usado quando o motorista/gestor não tem GPS ou digita manualmente).
  async coordenadasPorEndereco(via, cidade) {
    const query = [via, cidade, 'Brasil'].filter(Boolean).join(', ');
    if (!query) return null;
    try {
      const resp = await fetch(
        `https://nominatim.openstreetmap.org/search?format=jsonv2&q=${encodeURIComponent(query)}&countrycodes=br&limit=1`
      );
      if (!resp.ok) return null;
      const data = await resp.json();
      if (!data.length) return null;
      return { lat: data[0].lat, lon: data[0].lon };
    } catch (e) {
      return null;
    }
  },
};
