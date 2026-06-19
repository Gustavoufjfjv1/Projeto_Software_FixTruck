/**
 * Módulo de Autenticação
 * Gerencia login, registro e sessão de usuários
 */

class AuthManager {
    constructor() {
        this.usuarioAtual = this.carregarUsuarioSalvo();
    }

    /**
     * Carrega o usuário do localStorage se existir
     */
    carregarUsuarioSalvo() {
        const usuario = localStorage.getItem('usuario_atual');
        return usuario ? JSON.parse(usuario) : null;
    }

    /**
     * Realiza login
     */
    async login(email, senha) {
        try {
            const resposta = await apiClient.login(email, senha);

            // Salvar dados do usuário
            this.usuarioAtual = resposta.usuario;
            localStorage.setItem('usuario_atual', JSON.stringify(resposta.usuario));
            localStorage.setItem('auth_token', resposta.token);

            return resposta;
        } catch (erro) {
            throw erro;
        }
    }

    /**
     * Realiza registro de novo usuário
     */
    async registrar(nome, email, senha, tipoUsuario, dadosAdicionais = {}) {
        try {
            const resposta = await apiClient.registrar(nome, email, senha, tipoUsuario, dadosAdicionais);
            return resposta;
        } catch (erro) {
            throw erro;
        }
    }

    /**
     * Realiza logout
     */
    logout() {
        this.usuarioAtual = null;
        localStorage.removeItem('usuario_atual');
        localStorage.removeItem('auth_token');
        apiClient.token = null;
    }

    /**
     * Verifica se está autenticado
     */
    estaAutenticado() {
        return this.usuarioAtual !== null && localStorage.getItem('auth_token') !== null;
    }

    /**
     * Obtém o usuário atual
     */
    obterUsuarioAtual() {
        return this.usuarioAtual;
    }

    /**
     * Obtém o tipo de usuário atual
     */
    obterTipoUsuario() {
        return this.usuarioAtual?.tipo_usuario || null;
    }

    /**
     * Verifica se o usuário é gestor
     */
    ehGestor() {
        return this.obterTipoUsuario() === 'gestor';
    }

    /**
     * Verifica se o usuário é motorista
     */
    ehMotorista() {
        return this.obterTipoUsuario() === 'motorista';
    }

    /**
     * Altera a senha do usuário
     */
    async alterarSenha(senhaAtual, senhaNova) {
        try {
            const resultado = await apiClient.alterarSenha(
                this.usuarioAtual.id_usuario,
                senhaAtual,
                senhaNova
            );
            return resultado;
        } catch (erro) {
            throw erro;
        }
    }
}

// Instância global do gerenciador de autenticação
const authManager = new AuthManager();
