/**
 * Router para navegação entre páginas
 * Gerencia as rotas da aplicação
 */

class Router {
    constructor() {
        this.rotasPublicas = ['/', '/login', '/registrar'];
        this.rotasGestor = ['/gestor'];
        this.rotasMotorista = ['/motorista'];
        this.rotaAtual = '/';
    }

    /**
     * Verifica se a rota é pública
     */
    ehPublica(rota) {
        return this.rotasPublicas.some(r => rota.startsWith(r));
    }

    /**
     * Verifica se a rota requer autenticação de gestor
     */
    ehRotaGestor(rota) {
        return this.rotasGestor.some(r => rota.startsWith(r));
    }

    /**
     * Verifica se a rota requer autenticação de motorista
     */
    ehRotaMotorista(rota) {
        return this.rotasMotorista.some(r => rota.startsWith(r));
    }

    /**
     * Navega para uma rota
     */
    navegar(rota) {
        // Verificar autenticação
        if (!this.ehPublica(rota) && !authManager.estaAutenticado()) {
            this.rotaAtual = '/login';
            return;
        }

        // Verificar permissões
        if (this.ehRotaGestor(rota) && !authManager.ehGestor()) {
            console.warn('Acesso negado: permissão de gestor necessária');
            return;
        }

        if (this.ehRotaMotorista(rota) && !authManager.ehMotorista()) {
            console.warn('Acesso negado: permissão de motorista necessária');
            return;
        }

        this.rotaAtual = rota;
        this.renderizar();
    }

    /**
     * Renderiza a página atual
     */
    renderizar() {
        const app = document.getElementById('app');

        // Limpar conteúdo anterior
        app.innerHTML = '';

        switch (this.rotaAtual) {
            case '/':
                this.renderizarHome(app);
                break;
            case '/login':
                this.renderizarLogin(app);
                break;
            case '/registrar':
                this.renderizarRegistro(app);
                break;
            case '/gestor':
                if (authManager.ehGestor()) {
                    gestorApp.renderizar(app);
                }
                break;
            case '/motorista':
                if (authManager.ehMotorista()) {
                    motoristaApp.renderizar(app);
                }
                break;
            default:
                this.renderizarHome(app);
        }
    }

    /**
     * Renderiza página inicial
     */
    renderizarHome(app) {
        app.innerHTML = `
            <div class="navbar">
                <div class="navbar-content">
                    <div class="navbar-brand">
                        <i class="fas fa-truck"></i>
                        FixTruck
                    </div>
                    <div class="navbar-menu">
                        <button class="btn btn-primary" onclick="router.navegar('/login')">
                            <i class="fas fa-sign-in-alt"></i>
                            Login
                        </button>
                        <button class="btn btn-secondary" onclick="router.navegar('/registrar')">
                            <i class="fas fa-user-plus"></i>
                            Registrar
                        </button>
                    </div>
                </div>
            </div>

            <div class="main-content">
                <div class="page-header">
                    <h1 class="page-title">Bem-vindo ao FixTruck</h1>
                    <p class="page-subtitle">Sistema de Gestão de Ocorrências Mecânicas para Frotas Rodoviárias</p>
                </div>

                <div class="card">
                    <div class="card-body">
                        <h2>O que é FixTruck?</h2>
                        <p>FixTruck é uma plataforma moderna para otimizar a gestão de ocorrências mecânicas em frotas rodoviárias.</p>
                        
                        <h3 style="margin-top: 2rem;">Funcionalidades Principais:</h3>
                        <ul style="margin-left: 1.5rem; margin-top: 1rem;">
                            <li>Registro rápido de ocorrências com localização GPS</li>
                            <li>Busca de oficinas próximas em mapa interativo</li>
                            <li>Orçamentos e aprovação digital</li>
                            <li>Chat em tempo real entre equipes</li>
                            <li>Histórico completo de ocorrências</li>
                        </ul>

                        <div class="mt-4">
                            <button class="btn btn-primary btn-block" onclick="router.navegar('/login')">
                                Fazer Login
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        `;
    }

    /**
     * Renderiza página de login
     */
    renderizarLogin(app) {
        app.innerHTML = `
            <div class="navbar">
                <div class="navbar-content">
                    <div class="navbar-brand">
                        <i class="fas fa-truck"></i>
                        FixTruck
                    </div>
                </div>
            </div>

            <div class="main-content">
                <div class="card" style="max-width: 400px; margin: 3rem auto;">
                    <div class="card-header">
                        <h1 class="card-title">Login</h1>
                    </div>

                    <div class="card-body">
                        <form id="formLogin">
                            <div class="form-group">
                                <label class="form-label">Email</label>
                                <input type="email" class="form-control" id="email" required>
                            </div>

                            <div class="form-group">
                                <label class="form-label">Senha</label>
                                <input type="password" class="form-control" id="senha" required>
                            </div>

                            <button type="submit" class="btn btn-primary btn-block">
                                Entrar
                            </button>
                        </form>

                        <div style="text-align: center; margin-top: 1rem;">
                            <p>Não tem conta? <a href="#" onclick="router.navegar('/registrar'); return false;">Registre-se aqui</a></p>
                        </div>
                    </div>
                </div>
            </div>
        `;

        document.getElementById('formLogin').addEventListener('submit', async (e) => {
            e.preventDefault();
            
            const email = document.getElementById('email').value;
            const senha = document.getElementById('senha').value;

            try {
                await authManager.login(email, senha);
                
                // Redirecionar para dashboard apropriado
                if (authManager.ehGestor()) {
                    router.navegar('/gestor');
                } else if (authManager.ehMotorista()) {
                    router.navegar('/motorista');
                }
            } catch (erro) {
                alert('Erro ao fazer login: ' + erro.message);
            }
        });
    }

    /**
     * Renderiza página de registro
     */
    renderizarRegistro(app) {
        app.innerHTML = `
            <div class="navbar">
                <div class="navbar-content">
                    <div class="navbar-brand">
                        <i class="fas fa-truck"></i>
                        FixTruck
                    </div>
                </div>
            </div>

            <div class="main-content">
                <div class="card" style="max-width: 400px; margin: 2rem auto;">
                    <div class="card-header">
                        <h1 class="card-title">Registrar</h1>
                    </div>

                    <div class="card-body">
                        <form id="formRegistro">
                            <div class="form-group">
                                <label class="form-label">Nome</label>
                                <input type="text" class="form-control" id="nome" required>
                            </div>

                            <div class="form-group">
                                <label class="form-label">Email</label>
                                <input type="email" class="form-control" id="email" required>
                            </div>

                            <div class="form-group">
                                <label class="form-label">Senha</label>
                                <input type="password" class="form-control" id="senha" required>
                            </div>

                            <div class="form-group">
                                <label class="form-label">Tipo de Usuário</label>
                                <select class="form-control" id="tipoUsuario" required>
                                    <option value="">Selecione...</option>
                                    <option value="gestor">Gestor</option>
                                    <option value="motorista">Motorista</option>
                                </select>
                            </div>

                            <button type="submit" class="btn btn-primary btn-block">
                                Registrar
                            </button>
                        </form>

                        <div style="text-align: center; margin-top: 1rem;">
                            <p>Já tem conta? <a href="#" onclick="router.navegar('/login'); return false;">Faça login aqui</a></p>
                        </div>
                    </div>
                </div>
            </div>
        `;

        document.getElementById('formRegistro').addEventListener('submit', async (e) => {
            e.preventDefault();

            const nome = document.getElementById('nome').value;
            const email = document.getElementById('email').value;
            const senha = document.getElementById('senha').value;
            const tipoUsuario = document.getElementById('tipoUsuario').value;

            try {
                await authManager.registrar(nome, email, senha, tipoUsuario);
                alert('Registrado com sucesso! Faça login agora.');
                router.navegar('/login');
            } catch (erro) {
                alert('Erro ao registrar: ' + erro.message);
            }
        });
    }
}

// Instância global do router
const router = new Router();
