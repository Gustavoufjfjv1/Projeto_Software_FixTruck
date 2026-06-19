/**
 * API Client para comunicação com o backend
 * Handles todas as requisições HTTP para a API REST
 */

const API_BASE_URL = 'http://localhost:5000/api';

class APIClient {
    constructor() {
        this.token = localStorage.getItem('auth_token');
    }

    /**
     * Faz uma requisição para a API
     */
    async request(endpoint, method = 'GET', data = null) {
        const headers = {
            'Content-Type': 'application/json',
        };

        if (this.token) {
            headers['Authorization'] = `Bearer ${this.token}`;
        }

        const options = {
            method,
            headers,
        };

        if (data) {
            options.body = JSON.stringify(data);
        }

        try {
            const response = await fetch(`${API_BASE_URL}${endpoint}`, options);

            if (!response.ok) {
                const error = await response.json();
                throw new Error(error.erro || `Erro HTTP: ${response.status}`);
            }

            return await response.json();
        } catch (error) {
            console.error('Erro na requisição:', error);
            throw error;
        }
    }

    // Auth endpoints
    async registrar(nome, email, senha, tipoUsuario, dadosAdicionais = {}) {
        return this.request('/auth/registrar', 'POST', {
            nome,
            email,
            senha,
            tipo_usuario: tipoUsuario,
            dados_adicionais: dadosAdicionais
        });
    }

    async login(email, senha) {
        const response = await this.request('/auth/login', 'POST', { email, senha });
        if (response.token) {
            this.token = response.token;
            localStorage.setItem('auth_token', response.token);
        }
        return response;
    }

    async alterarSenha(idUsuario, senhaAtual, senhaNova) {
        return this.request('/auth/alterar-senha', 'POST', {
            id_usuario: idUsuario,
            senha_atual: senhaAtual,
            senha_nova: senhaNova
        });
    }

    // Usuários
    async obterUsuario(idUsuario) {
        return this.request(`/usuarios/${idUsuario}`);
    }

    async listarUsuarios(tipoUsuario = null) {
        let endpoint = '/usuarios';
        if (tipoUsuario) {
            endpoint += `?tipo_usuario=${tipoUsuario}`;
        }
        return this.request(endpoint);
    }

    async atualizarUsuario(idUsuario, dados) {
        return this.request(`/usuarios/${idUsuario}`, 'PUT', dados);
    }

    async deletarUsuario(idUsuario) {
        return this.request(`/usuarios/${idUsuario}`, 'DELETE');
    }

    // Veículos
    async criarVeiculo(placa, modelo, marca, tipoVeiculo, idEmpresa) {
        return this.request('/veiculos', 'POST', {
            placa,
            modelo,
            marca,
            tipo_veiculo: tipoVeiculo,
            id_empresa: idEmpresa
        });
    }

    async obterVeiculo(idVeiculo) {
        return this.request(`/veiculos/${idVeiculo}`);
    }

    async listarVeiculos(idEmpresa = null) {
        let endpoint = '/veiculos';
        if (idEmpresa) {
            endpoint += `?id_empresa=${idEmpresa}`;
        }
        return this.request(endpoint);
    }

    async obterHistoricoOcorrencias(idVeiculo, limite = null) {
        let endpoint = `/veiculos/${idVeiculo}/historico-ocorrencias`;
        if (limite) {
            endpoint += `?limite=${limite}`;
        }
        return this.request(endpoint);
    }

    async atualizarVeiculo(idVeiculo, dados) {
        return this.request(`/veiculos/${idVeiculo}`, 'PUT', dados);
    }

    // Ocorrências
    async criarOcorrencia(idVeiculo, tipoProblema, latitude, longitude, dados = {}) {
        return this.request('/ocorrencias', 'POST', {
            id_veiculo: idVeiculo,
            tipo_problema: tipoProblema,
            latitude,
            longitude,
            ...dados
        });
    }

    async obterOcorrencia(idOcorrencia) {
        return this.request(`/ocorrencias/${idOcorrencia}`);
    }

    async listarOcorrencias(filtros = {}) {
        let endpoint = '/ocorrencias?';
        if (filtros.status) endpoint += `status=${filtros.status}&`;
        if (filtros.idVeiculo) endpoint += `id_veiculo=${filtros.idVeiculo}&`;
        if (filtros.idOficina) endpoint += `id_oficina=${filtros.idOficina}&`;
        endpoint = endpoint.replace(/&$/, '');

        return this.request(endpoint);
    }

    async vincularOficina(idOcorrencia, idOficina) {
        return this.request(`/ocorrencias/${idOcorrencia}/vincular-oficina`, 'PUT', {
            id_oficina: idOficina
        });
    }

    async encerrarOcorrencia(idOcorrencia, motivoResolucao, observacao = '') {
        return this.request(`/ocorrencias/${idOcorrencia}/encerrar`, 'PUT', {
            motivo_resolucao: motivoResolucao,
            observacao
        });
    }

    async obterDowntime(idOcorrencia) {
        return this.request(`/ocorrencias/${idOcorrencia}/downtime`);
    }

    // Oficinas
    async criarOficina(dados) {
        return this.request('/oficinas', 'POST', dados);
    }

    async obterOficina(idOficina) {
        return this.request(`/oficinas/${idOficina}`);
    }

    async buscarOficinasPorRaio(latitude, longitude, raioKm, filtros = {}) {
        return this.request('/oficinas/buscar-por-raio', 'POST', {
            latitude,
            longitude,
            raio_km: raioKm,
            ...filtros
        });
    }

    async listarOficinas(filtros = {}) {
        let endpoint = '/oficinas?';
        if (filtros.ativo !== undefined) endpoint += `ativo=${filtros.ativo}&`;
        if (filtros.especialidade) endpoint += `especialidade=${filtros.especialidade}&`;
        endpoint = endpoint.replace(/&$/, '');

        return this.request(endpoint);
    }

    async atualizarOficina(idOficina, dados) {
        return this.request(`/oficinas/${idOficina}`, 'PUT', dados);
    }

    async atualizarStatusOficina(idOficina, status) {
        return this.request(`/oficinas/${idOficina}/status`, 'PUT', { status });
    }

    // Orçamentos
    async criarOrcamento(idOcorrencia, idOficina, valorPecas, valorMaoObra, observacoes = '') {
        return this.request('/orcamentos', 'POST', {
            id_ocorrencia: idOcorrencia,
            id_oficina: idOficina,
            valor_pecas: valorPecas,
            valor_mao_obra: valorMaoObra,
            observacoes
        });
    }

    async obterOrcamento(idOrcamento) {
        return this.request(`/orcamentos/${idOrcamento}`);
    }

    async listarOrcamentosOcorrencia(idOcorrencia) {
        return this.request(`/orcamentos/ocorrencia/${idOcorrencia}`);
    }

    async aprovarOrcamento(idOrcamento) {
        return this.request(`/orcamentos/${idOrcamento}/aprovar`, 'PUT');
    }

    async rejeitarOrcamento(idOrcamento, observacoes = '') {
        return this.request(`/orcamentos/${idOrcamento}/rejeitar`, 'PUT', { observacoes });
    }

    // Chat
    async enviarMensagem(idOcorrencia, idUsuario, texto, fotoEvidencia = null) {
        return this.request(`/chat/${idOcorrencia}/mensagens`, 'POST', {
            id_usuario: idUsuario,
            texto,
            url_foto_evidencia: fotoEvidencia
        });
    }

    async obterMensagens(idOcorrencia) {
        return this.request(`/chat/${idOcorrencia}/mensagens`);
    }

    async obterHistoricoChat(idOcorrencia, limite = null) {
        let endpoint = `/chat/${idOcorrencia}/historico`;
        if (limite) {
            endpoint += `?limite=${limite}`;
        }
        return this.request(endpoint);
    }

    // Health Check
    async verificarSaude() {
        try {
            const response = await fetch(`${API_BASE_URL.replace('/api', '')}/health`);
            return response.ok;
        } catch {
            return false;
        }
    }
}

// Instância global do cliente API
const apiClient = new APIClient();
