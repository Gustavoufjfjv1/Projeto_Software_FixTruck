/**
 * Aplicação do Motorista
 * Interface específica para motoristas
 */

class MotoristaApp {
    constructor() {
        this.mapaOcorrencia = null;
        this.ocorrenciaAtual = null;
        this.oficinasProximas = [];
    }

    /**
     * Renderiza a interface do motorista
     */
    renderizar(app) {
        app.innerHTML = `
            <div class="navbar">
                <div class="navbar-content">
                    <div class="navbar-brand">
                        <i class="fas fa-truck"></i>
                        FixTruck - Motorista
                    </div>
                    <div class="navbar-menu">
                        <span>${authManager.obterUsuarioAtual().nome}</span>
                        <button class="btn btn-secondary btn-sm" onclick="authManager.logout(); router.navegar('/')">
                            Sair
                        </button>
                    </div>
                </div>
            </div>

            <div style="display: flex;">
                <div class="sidebar">
                    <ul class="sidebar-menu">
                        <li class="sidebar-menu-item">
                            <a href="#" onclick="motoristaApp.mostrarNovaOcorrencia(); return false;" class="active">
                                <i class="fas fa-exclamation-triangle"></i>
                                Nova Ocorrência
                            </a>
                        </li>
                        <li class="sidebar-menu-item">
                            <a href="#" onclick="motoristaApp.mostrarOcorrenciasAbertas(); return false;">
                                <i class="fas fa-clipboard-list"></i>
                                Ocorrências Abertas
                            </a>
                        </li>
                        <li class="sidebar-menu-item">
                            <a href="#" onclick="motoristaApp.mostrarHistorico(); return false;">
                                <i class="fas fa-history"></i>
                                Histórico
                            </a>
                        </li>
                    </ul>
                </div>

                <div class="main-content">
                    <div id="conteudo-motorista"></div>
                </div>
            </div>
        `;

        // Mostrar tela inicial
        this.mostrarNovaOcorrencia();
    }

    /**
     * Mostra formulário para nova ocorrência
     */
    mostrarNovaOcorrencia() {
        const conteudo = document.getElementById('conteudo-motorista');

        conteudo.innerHTML = `
            <div class="page-header">
                <h1 class="page-title">Registrar Nova Ocorrência</h1>
                <p class="page-subtitle">Informe o problema mecânico encontrado</p>
            </div>

            <div class="card">
                <div class="card-header">
                    <h2 class="card-title">Formulário de Ocorrência</h2>
                </div>

                <div class="card-body">
                    <form id="formOcorrencia">
                        <div class="form-group">
                            <label class="form-label">Tipo de Problema</label>
                            <select class="form-control" id="tipoProblema" required>
                                <option value="">Selecione...</option>
                                <option value="mecanico">Problema Mecânico</option>
                                <option value="hidraulico">Problema Hidráulico</option>
                                <option value="eletrico">Problema Elétrico</option>
                                <option value="pneu">Problema com Pneu</option>
                                <option value="combustivel">Problema de Combustível</option>
                                <option value="outro">Outro</option>
                            </select>
                        </div>

                        <div class="form-group">
                            <label class="form-label">Observações</label>
                            <textarea class="form-control" id="observacoes" placeholder="Descreva o problema em detalhes"></textarea>
                        </div>

                        <button type="submit" class="btn btn-primary btn-block">
                            Registrar Ocorrência
                        </button>
                    </form>
                </div>
            </div>

            <div id="mapa-container" class="card">
                <div class="card-header">
                    <h2 class="card-title">Oficinas Próximas</h2>
                </div>
                <div class="map-container" id="mapa-oficinas"></div>
            </div>
        `;

        document.getElementById('formOcorrencia').addEventListener('submit', async (e) => {
            e.preventDefault();
            
            // Obter localização do usuário
            if (navigator.geolocation) {
                navigator.geolocation.getCurrentPosition(async (position) => {
                    const latitude = position.coords.latitude;
                    const longitude = position.coords.longitude;

                    try {
                        const ocorrencia = await apiClient.criarOcorrencia(
                            authManager.obterUsuarioAtual().id_usuario,
                            document.getElementById('tipoProblema').value,
                            latitude,
                            longitude,
                            { observacao: document.getElementById('observacoes').value }
                        );

                        this.ocorrenciaAtual = ocorrencia;
                        this.carregarOficinasPorRaio(latitude, longitude);
                        alert('Ocorrência registrada com sucesso!');
                    } catch (erro) {
                        alert('Erro ao registrar ocorrência: ' + erro.message);
                    }
                });
            } else {
                alert('Geolocalização não disponível no seu navegador');
            }
        });

        // Inicializar mapa
        this.inicializarMapa();
    }

    /**
     * Inicializa o mapa interativo
     */
    inicializarMapa() {
        const container = document.getElementById('mapa-oficinas');
        if (!container) return;

        this.mapaOcorrencia = L.map('mapa-oficinas').setView([-19.9166, -43.9345], 13);

        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
            attribution: '© OpenStreetMap contributors',
            maxZoom: 19
        }).addTo(this.mapaOcorrencia);
    }

    /**
     * Carrega oficinas próximas por raio
     */
    async carregarOficinasPorRaio(latitude, longitude, raioKm = 10) {
        try {
            const oficinas = await apiClient.buscarOficinasPorRaio(latitude, longitude, raioKm);
            this.oficinasProximas = oficinas;

            // Adicionar marcadores ao mapa
            if (this.mapaOcorrencia) {
                // Adicionar marcador da localização do motorista
                L.marker([latitude, longitude], {
                    icon: L.icon({
                        iconUrl: 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-blue.png',
                        iconSize: [25, 41],
                        iconAnchor: [12, 41]
                    })
                }).addTo(this.mapaOcorrencia).bindPopup('Sua Localização');

                // Adicionar marcadores das oficinas
                oficinas.forEach(oficina => {
                    L.marker([oficina.latitude, oficina.longitude], {
                        icon: L.icon({
                            iconUrl: 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-red.png',
                            iconSize: [25, 41],
                            iconAnchor: [12, 41]
                        })
                    }).addTo(this.mapaOcorrencia).bindPopup(`
                        <strong>${oficina.nome_fantasia}</strong><br>
                        Distância: ${oficina.distancia_km}km<br>
                        <button class="btn btn-sm btn-primary" onclick="motoristaApp.selecionarOficina(${oficina.id_oficina})">
                            Selecionar
                        </button>
                    `);
                });
            }
        } catch (erro) {
            console.error('Erro ao carregar oficinas:', erro);
        }
    }

    /**
     * Seleciona uma oficina
     */
    async selecionarOficina(idOficina) {
        try {
            if (this.ocorrenciaAtual) {
                const resultado = await apiClient.vincularOficina(
                    this.ocorrenciaAtual.id_ocorrencia,
                    idOficina
                );

                alert('Oficina selecionada com sucesso!');
                this.mostrarDetalhesOcorrencia(resultado);
            }
        } catch (erro) {
            alert('Erro ao selecionar oficina: ' + erro.message);
        }
    }

    /**
     * Mostra detalhes da ocorrência
     */
    mostrarDetalhesOcorrencia(ocorrencia) {
        const conteudo = document.getElementById('conteudo-motorista');

        conteudo.innerHTML = `
            <div class="page-header">
                <h1 class="page-title">Ocorrência #${ocorrencia.id_ocorrencia}</h1>
                <p class="page-subtitle">Status: <span class="badge badge-info">${ocorrencia.status}</span></p>
            </div>

            <div class="card">
                <div class="card-header">
                    <h2 class="card-title">Detalhes da Ocorrência</h2>
                </div>

                <div class="card-body">
                    <p><strong>Tipo de Problema:</strong> ${ocorrencia.tipo_problema}</p>
                    <p><strong>Data de Abertura:</strong> ${new Date(ocorrencia.data_abertura).toLocaleString()}</p>
                    <p><strong>Localização:</strong> ${ocorrencia.latitude}, ${ocorrencia.longitude}</p>
                </div>
            </div>

            <div id="chat-container"></div>
        `;

        this.carregarChat(ocorrencia.id_ocorrencia);
    }

    /**
     * Carrega o chat da ocorrência
     */
    async carregarChat(idOcorrencia) {
        try {
            const mensagens = await apiClient.obterMensagens(idOcorrencia);

            const chatContainer = document.getElementById('chat-container');
            chatContainer.innerHTML = `
                <div class="card">
                    <div class="card-header">
                        <h2 class="card-title">Chat</h2>
                    </div>

                    <div class="card-body">
                        <div id="mensagens" style="height: 400px; overflow-y: auto; border: 1px solid var(--border-color); padding: 1rem; margin-bottom: 1rem;">
                            ${mensagens.map(msg => `
                                <div style="margin-bottom: 1rem;">
                                    <strong>${msg.autor.nome}</strong>
                                    <p>${msg.texto}</p>
                                    <small style="color: var(--text-light);">${new Date(msg.data_hora).toLocaleString()}</small>
                                </div>
                            `).join('')}
                        </div>

                        <form id="formMensagem">
                            <div style="display: flex; gap: 0.5rem;">
                                <input type="text" id="textoMensagem" class="form-control" placeholder="Digite sua mensagem..." required>
                                <button type="submit" class="btn btn-primary">Enviar</button>
                            </div>
                        </form>
                    </div>
                </div>
            `;

            document.getElementById('formMensagem').addEventListener('submit', async (e) => {
                e.preventDefault();

                const texto = document.getElementById('textoMensagem').value;

                try {
                    await apiClient.enviarMensagem(
                        idOcorrencia,
                        authManager.obterUsuarioAtual().id_usuario,
                        texto
                    );

                    document.getElementById('textoMensagem').value = '';
                    this.carregarChat(idOcorrencia);
                } catch (erro) {
                    alert('Erro ao enviar mensagem: ' + erro.message);
                }
            });
        } catch (erro) {
            console.error('Erro ao carregar chat:', erro);
        }
    }

    /**
     * Mostra ocorrências abertas
     */
    async mostrarOcorrenciasAbertas() {
        try {
            const ocorrencias = await apiClient.listarOcorrencias({ status: 'aberta' });

            const conteudo = document.getElementById('conteudo-motorista');

            conteudo.innerHTML = `
                <div class="page-header">
                    <h1 class="page-title">Ocorrências Abertas</h1>
                </div>

                <div class="card">
                    <div class="card-body">
                        ${ocorrencias.length === 0 ? '<p>Nenhuma ocorrência aberta</p>' : `
                            <table class="table">
                                <thead>
                                    <tr>
                                        <th>ID</th>
                                        <th>Tipo de Problema</th>
                                        <th>Data</th>
                                        <th>Status</th>
                                        <th>Ações</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    ${ocorrencias.map(oc => `
                                        <tr>
                                            <td>#${oc.id_ocorrencia}</td>
                                            <td>${oc.tipo_problema}</td>
                                            <td>${new Date(oc.data_abertura).toLocaleDateString()}</td>
                                            <td><span class="badge badge-info">${oc.status}</span></td>
                                            <td>
                                                <button class="btn btn-primary btn-sm" onclick="motoristaApp.abrirOcorrencia(${oc.id_ocorrencia})">
                                                    Ver Detalhes
                                                </button>
                                            </td>
                                        </tr>
                                    `).join('')}
                                </tbody>
                            </table>
                        `}
                    </div>
                </div>
            `;
        } catch (erro) {
            alert('Erro ao carregar ocorrências: ' + erro.message);
        }
    }

    /**
     * Abre uma ocorrência específica
     */
    async abrirOcorrencia(idOcorrencia) {
        try {
            const ocorrencia = await apiClient.obterOcorrencia(idOcorrencia);
            this.mostrarDetalhesOcorrencia(ocorrencia);
        } catch (erro) {
            alert('Erro ao abrir ocorrência: ' + erro.message);
        }
    }

    /**
     * Mostra histórico de ocorrências
     */
    async mostrarHistorico() {
        try {
            const ocorrencias = await apiClient.listarOcorrencias({});

            const conteudo = document.getElementById('conteudo-motorista');

            conteudo.innerHTML = `
                <div class="page-header">
                    <h1 class="page-title">Histórico de Ocorrências</h1>
                </div>

                <div class="card">
                    <div class="card-body">
                        ${ocorrencias.length === 0 ? '<p>Nenhuma ocorrência registrada</p>' : `
                            <table class="table">
                                <thead>
                                    <tr>
                                        <th>ID</th>
                                        <th>Problema</th>
                                        <th>Data Abertura</th>
                                        <th>Status</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    ${ocorrencias.map(oc => `
                                        <tr>
                                            <td>#${oc.id_ocorrencia}</td>
                                            <td>${oc.tipo_problema}</td>
                                            <td>${new Date(oc.data_abertura).toLocaleDateString()}</td>
                                            <td><span class="badge badge-${oc.status === 'resolvida' ? 'success' : 'info'}">${oc.status}</span></td>
                                        </tr>
                                    `).join('')}
                                </tbody>
                            </table>
                        `}
                    </div>
                </div>
            `;
        } catch (erro) {
            alert('Erro ao carregar histórico: ' + erro.message);
        }
    }
}

// Instância global da aplicação do motorista
const motoristaApp = new MotoristaApp();
