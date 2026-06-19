/**
 * Aplicação Principal - FixTruck
 * Ponto de entrada da aplicação
 */

document.addEventListener('DOMContentLoaded', async () => {
    // Verificar saúde da API
    const apiOk = await apiClient.verificarSaude();
    
    if (!apiOk) {
        console.warn('⚠️ API não está respondendo. Verifique se o backend está rodando em http://localhost:5000');
    }

    // Verificar se usuário está autenticado
    if (authManager.estaAutenticado()) {
        if (authManager.ehGestor()) {
            router.navegar('/gestor');
        } else if (authManager.ehMotorista()) {
            router.navegar('/motorista');
        }
    } else {
        router.navegar('/');
    }
});

// Prevenir navegação do navegador se estiver usando a aplicação
window.addEventListener('beforeunload', (e) => {
    // Permitir reload apenas em desenvolvimento
    // Em produção, você pode implementar um PWA para melhor experiência offline
});
