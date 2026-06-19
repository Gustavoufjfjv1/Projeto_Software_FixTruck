/**
 * Aplicação do Gestor
 * Interface específica para gestores
 */

class GestorApp {
    constructor() {
        this.ocorrenciaAtual = null;
    }

    /**
     * Renderiza a interface do gestor
     */
    renderizar(app) {
        app.innerHTML = `
            <div class="navbar">
                <div class="navbar-content">
                    <div class="navbar-brand">
                        <i class="fas fa-truck"></i>
                        FixTruck - Gestor
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
                            <a href="#" onclick="gestorApp.mostrarDashboard(); return false;" class="active">
                                <i class="fas fa-chart-line"></i>
                                Dashboard
                            </a>
                        </li>
                        <li class="sidebar-menu-item">
                            <a href="#" onclick="gestorApp.mostrarOcorrenciasAbertas(); return false;">
                                <i class="fas fa-exclamation-triangle"></i>
                                Ocorrências Abertas
                            </a>
                        </li>
                        <li class="sidebar-menu-item">
                            <a href="#" onclick="gestorApp.mostrarOrcamentos(); return false;">
                                <i class="fas fa-file-invoice-dollar"></i>
                                Orçamentos
                            </a>
                        </li>
                        <li class="sidebar-menu-item">
                            <a href="#" onclick="gestorApp.mostrarHistorico(); return false;">
                                <i class="fas fa-history"></i>
                                Histórico
                            </a>
                        </li>
                    </ul>
                </div>

                <div class="main-content">
                    <div id="conteudo-gestor"></div>
                </div>
            </div>
        `;

        // Mostrar dashboard inicial
        this.mostrarDashboard();
    }

    /**
     * Mostra o dashboard
     */
    async mostrarDashboard() {
        try {
            const ocorrenciasAbertas = await apiClient.listarOcorrencias({ status: 'aberta' });
            const ocorrenciasEmAtendimento = await apiClient.listarOcorrencias({ status: 'em_atendimento' });

            const conteudo = document.getElementById('conteudo-gestor');

            conteudo.innerHTML = `
                <div class="page-header">
                    <h1 class="page-title">Dashboard</h1>
                    <p class="page-subtitle">Visão geral das operações</p>
                </div>

                <div class="grid grid-3">
                    <div class="card">
                        <div class="card-body text-center">
                            <h3 style="font-size: 2rem; color: var(--primary-color);">
                                ${ocorrenciasAbertas.length}
                            </h3>
                            <p>Ocorrências Abertas</p>
                        </div>
                    </div>

                    <div class="card">
                        <div class="card-body text-center">
                            <h3 style="font-size: 2rem; color: var(--warning-color);">
                                ${ocorrenciasEmAtendimento.length}
                            </h3>
                            <p>Em Atendimento</p>
                        </div>
                    </div>

                    <div class="card">
                        <div class="card-body text-center">
                            <h3 style="font-size: 2rem; color: var(--success-color);">
                                -
                            </h3>
                            <p>Resolvidas (Esta Semana)</p>
                        </div>
                    </div>
                </div>

                <div class="card">
                    <div class="card-header">
                        <h2 class="card-title">Ocorrências Recentes</h2>
                    </div>

                    <div class="card-body">
                        ${ocorrenciasAbertas.length === 0 ? '<p>Nenhuma ocorrência aberta</p>' : `
                            <table class="table">
                                <thead>
                                    <tr>
                                        <th>ID</th>
                                        <th>Problema</th>
                                        <th>Data</th>
                                        <th>Status</th>
                                        <th>Ações</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    ${ocorrenciasAbertas.map(oc => `
                                        <tr>
                                            <td>#${oc.id_ocorrencia}</td>
                                            <td>${oc.tipo_problema}</td>
                                            <td>${new Date(oc.data_abertura).toLocaleDateString()}</td>
                                            <td><span class="badge badge-warning">${oc.status}</span></td>
                                            <td>
                                                <button class="btn btn-primary btn-sm" onclick="gestorApp.abrirOcorrencia(${oc.id_ocorrencia})">
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
            alert('Erro ao carregar dashboard: ' + erro.message);
        }
    }

    /**
     * Mostra ocorrências abertas
     */
    async mostrarOcorrenciasAbertas() {
        try {
            const ocorrencias = await apiClient.listarOcorrencias({ status: 'aberta' });

            const conteudo = document.getElementById('conteudo-gestor');

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
                                        <th>Tipo</th>
                                        <th>Data</th>
                                        <th>Veículo</th>
                                        <th>Ações</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    ${ocorrencias.map(oc => `
                                        <tr>
                                            <td>#${oc.id_ocorrencia}</td>
                                            <td>${oc.tipo_problema}</td>
                                            <td>${new Date(oc.data_abertura).toLocaleDateString()}</td>
                                            <td>${oc.veiculo ? oc.veiculo.placa : 'N/A'}</td>
                                            <td>
                                                <button class="btn btn-primary btn-sm" onclick="gestorApp.abrirOcorrencia(${oc.id_ocorrencia})">
                                                    Abrir
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
            const orcamentos = await apiClient.listarOrcamentosOcorrencia(idOcorrencia);

            const conteudo = document.getElementById('conteudo-gestor');

            conteudo.innerHTML = `
                <div class="page-header">
                    <h1 class="page-title">Ocorrência #${ocorrencia.id_ocorrencia}</h1>
                    <p class="page-subtitle">Status: <span class="badge badge-info">${ocorrencia.status}</span></p>
                </div>

                <div class="card">
                    <div class="card-header">
                        <h2 class="card-title">Detalhes</h2>
                    </div>

                    <div class="card-body">
                        <p><strong>Problema:</strong> ${ocorrencia.tipo_problema}</p>
                        <p><strong>Abertura:</strong> ${new Date(ocorrencia.data_abertura).toLocaleString()}</p>
                        <p><strong>Veículo:</strong> ${ocorrencia.veiculo ? ocorrencia.veiculo.placa : 'N/A'}</p>
                        <p><strong>Downtime:</strong> ${ocorrencia.downtime ? ocorrencia.downtime.toFixed(2) + ' horas' : 'Em andamento'}</p>
                    </div>
                </div>

                ${orcamentos.length > 0 ? `
                    <div class="card">
                        <div class="card-header">
                            <h2 class="card-title">Orçamentos</h2>
                        </div>

                        <div class="card-body">
                            <table class="table">
                                <thead>
                                    <tr>
                                        <th>ID</th>
                                        <th>Oficina</th>
                                        <th>Peças</th>
                                        <th>Mão de Obra</th>
                                        <th>Total</th>
                                        <th>Status</th>
                                        <th>Ações</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    ${orcamentos.map(orc => `
                                        <tr>
                                            <td>#${orc.id_orcamento}</td>
                                            <td>${orc.oficina ? orc.oficina.nome_fantasia : 'N/A'}</td>
                                            <td>R$ ${orc.valor_pecas.toFixed(2)}</td>
                                            <td>R$ ${orc.valor_mao_obra.toFixed(2)}</td>
                                            <td>R$ ${orc.valor_total.toFixed(2)}</td>
                                            <td><span class="badge badge-${orc.status_aprovacao === 'aprovado' ? 'success' : orc.status_aprovacao === 'rejeitado' ? 'danger' : 'warning'}">${orc.status_aprovacao}</span></td>
                                            <td>
                                                ${orc.status_aprovacao === 'pendente' ? `
                                                    <button class="btn btn-success btn-sm" onclick="gestorApp.aprovarOrcamento(${orc.id_orcamento})">
                                                        Aprovar
                                                    </button>
                                                    <button class="btn btn-danger btn-sm" onclick="gestorApp.rejeitarOrcamento(${orc.id_orcamento})">
                                                        Rejeitar
                                                    </button>
                                                ` : '-'}
                                            </td>
                                        </tr>
                                    `).join('')}
                                </tbody>
                            </table>
                        </div>
                    </div>
                ` : ''}

                <div class="card">
                    <div class="card-footer">
                        ${ocorrencia.status === 'aberta' || ocorrencia.status === 'em_atendimento' ? `
                            <button class="btn btn-success" onclick="gestorApp.encerrarOcorrencia(${ocorrencia.id_ocorrencia})">
                                Encerrar Ocorrência
                            </button>
                        ` : ''}
                        <button class="btn btn-secondary" onclick="gestorApp.mostrarDashboard()">
                            Voltar
                        </button>
                    </div>
                </div>
            `;
        } catch (erro) {
            alert('Erro ao abrir ocorrência: ' + erro.message);
        }
    }

    /**
     * Aprova um orçamento
     */
    async aprovarOrcamento(idOrcamento) {
        if (confirm('Deseja aprovar este orçamento?')) {
            try {
                await apiClient.aprovarOrcamento(idOrcamento);
                alert('Orçamento aprovado com sucesso!');
                // Recarregar a página
                location.reload();
            } catch (erro) {
                alert('Erro ao aprovar orçamento: ' + erro.message);
            }
        }
    }

    /**
     * Rejeita um orçamento
     */
    async rejeitarOrcamento(idOrcamento) {
        const motivo = prompt('Motivo da rejeição (opcional):');
        if (motivo !== null) {
            try {
                await apiClient.rejeitarOrcamento(idOrcamento, motivo);
                alert('Orçamento rejeitado com sucesso!');
                location.reload();
            } catch (erro) {
                alert('Erro ao rejeitar orçamento: ' + erro.message);
            }
        }
    }

    /**
     * Encerra uma ocorrência
     */
    async encerrarOcorrencia(idOcorrencia) {
        const motivo = prompt('Motivo da resolução:');
        if (motivo) {
            try {
                await apiClient.encerrarOcorrencia(idOcorrencia, motivo, '');
                alert('Ocorrência encerrada com sucesso!');
                this.mostrarDashboard();
            } catch (erro) {
                alert('Erro ao encerrar ocorrência: ' + erro.message);
            }
        }
    }

    /**
     * Mostra orçamentos pendentes
     */
    async mostrarOrcamentos() {
        try {
            const ocorrencias = await apiClient.listarOcorrencias({});
            const orcamentosPendentes = [];

            for (const oc of ocorrencias) {
                const orcamentos = await apiClient.listarOrcamentosOcorrencia(oc.id_ocorrencia);
                orcamentosPendentes.push(...orcamentos.filter(o => o.status_aprovacao === 'pendente'));
            }

            const conteudo = document.getElementById('conteudo-gestor');

            conteudo.innerHTML = `
                <div class="page-header">
                    <h1 class="page-title">Orçamentos Pendentes</h1>
                </div>

                <div class="card">
                    <div class="card-body">
                        ${orcamentosPendentes.length === 0 ? '<p>Nenhum orçamento pendente</p>' : `
                            <table class="table">
                                <thead>
                                    <tr>
                                        <th>ID</th>
                                        <th>Ocorrência</th>
                                        <th>Valor Total</th>
                                        <th>Ações</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    ${orcamentosPendentes.map(orc => `
                                        <tr>
                                            <td>#${orc.id_orcamento}</td>
                                            <td>#${orc.id_ocorrencia}</td>
                                            <td>R$ ${orc.valor_total.toFixed(2)}</td>
                                            <td>
                                                <button class="btn btn-success btn-sm" onclick="gestorApp.aprovarOrcamento(${orc.id_orcamento})">
                                                    Aprovar
                                                </button>
                                                <button class="btn btn-danger btn-sm" onclick="gestorApp.rejeitarOrcamento(${orc.id_orcamento})">
                                                    Rejeitar
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
            alert('Erro ao carregar orçamentos: ' + erro.message);
        }
    }

    /**
     * Mostra histórico de ocorrências
     */
    async mostrarHistorico() {
        try {
            const ocorrencias = await apiClient.listarOcorrencias({});
            const resolvidas = ocorrencias.filter(oc => oc.status === 'resolvida');

            const conteudo = document.getElementById('conteudo-gestor');

            conteudo.innerHTML = `
                <div class="page-header">
                    <h1 class="page-title">Histórico de Ocorrências Resolvidas</h1>
                </div>

                <div class="card">
                    <div class="card-body">
                        ${resolvidas.length === 0 ? '<p>Nenhuma ocorrência resolvida</p>' : `
                            <table class="table">
                                <thead>
                                    <tr>
                                        <th>ID</th>
                                        <th>Problema</th>
                                        <th>Data Abertura</th>
                                        <th>Data Fechamento</th>
                                        <th>Downtime</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    ${resolvidas.map(oc => `
                                        <tr>
                                            <td>#${oc.id_ocorrencia}</td>
                                            <td>${oc.tipo_problema}</td>
                                            <td>${new Date(oc.data_abertura).toLocaleDateString()}</td>
                                            <td>${oc.data_fechamento ? new Date(oc.data_fechamento).toLocaleDateString() : 'N/A'}</td>
                                            <td>${oc.downtime ? oc.downtime.toFixed(2) + 'h' : 'N/A'}</td>
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

// Instância global da aplicação do gestor
const gestorApp = new GestorApp();
