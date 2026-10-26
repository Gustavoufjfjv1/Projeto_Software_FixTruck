from services.erros import ServiceError
from services.cadastrar_empresa_service import CadastrarEmpresaService
from services.autenticar_empresa_service import AutenticarEmpresaService
from services.obter_empresa_autenticada_service import ObterEmpresaAutenticadaService
from services.recuperar_senha_service import RecuperarSenhaService
from services.redefinir_senha_service import RedefinirSenhaService
from services.obter_dashboard_service import ObterDashboardService
from services.listar_frota_service import ListarFrotaService
from services.cadastrar_motorista_service import CadastrarMotoristaService
from services.buscar_motoristas_service import BuscarMotoristasService
from services.atualizar_motorista_service import AtualizarMotoristaService
from services.inativar_motorista_service import InativarMotoristaService
from services.reativar_motorista_service import ReativarMotoristaService
from services.excluir_motorista_service import ExcluirMotoristaService
from services.cadastrar_veiculo_service import CadastrarVeiculoService
from services.atualizar_veiculo_service import AtualizarVeiculoService
from services.excluir_veiculo_service import ExcluirVeiculoService
from services.vincular_motorista_veiculo_service import VincularMotoristaVeiculoService
from services.listar_ocorrencias_service import ListarOcorrenciasService
from services.obter_dados_formulario_ocorrencia_service import ObterDadosFormularioOcorrenciaService
from services.registrar_ocorrencia_service import RegistrarOcorrenciaService
from services.atualizar_ocorrencia_service import AtualizarOcorrenciaService
from services.obter_detalhe_ocorrencia_service import ObterDetalheOcorrenciaService
from services.buscar_oficinas_para_ocorrencia_service import BuscarOficinasParaOcorrenciaService
from services.encerrar_ocorrencia_service import EncerrarOcorrenciaService
from services.atualizar_status_ocorrencia_service import AtualizarStatusOcorrenciaService
from services.vincular_oficina_ocorrencia_service import VincularOficinaOcorrenciaService
from services.listar_oficinas_service import ListarOficinasService
from services.obter_detalhe_oficina_service import ObterDetalheOficinaService
from services.favoritar_oficina_service import FavoritarOficinaService
from services.gerar_relatorio_service import GerarRelatorioService
from services.filtrar_relatorio_service import FiltrarRelatorioService
from services.gerar_relatorio_csv_service import GerarRelatorioCsvService
from services.reabrir_ocorrencia_service import ReabrirOcorrenciaService
from services.obter_perfil_service import ObterPerfilService
from services.atualizar_perfil_service import AtualizarPerfilService
from services.cadastrar_oficina_service import CadastrarOficinaService
from services.atualizar_oficina_service import (
    AtualizarOficinaService,
    AlterarStatusOficinaService,
    ListarMinhasOficinasService,
)
from services.acesso_motorista_service import (
    DefinirAcessoMotoristaService,
    AutenticarMotoristaService,
    TrocarSenhaMotoristaService,
    ObterPainelMotoristaService,
    ObterOcorrenciaMotoristaService,
    buscar_ocorrencia_do_motorista,
)
from services.buscar_oficinas_para_ocorrencia_service import buscar_oficinas_compativeis

__all__ = [
    'ServiceError',
    'CadastrarEmpresaService',
    'AutenticarEmpresaService',
    'ObterEmpresaAutenticadaService',
    'RecuperarSenhaService',
    'RedefinirSenhaService',
    'ObterDashboardService',
    'ListarFrotaService',
    'CadastrarMotoristaService',
    'BuscarMotoristasService',
    'AtualizarMotoristaService',
    'InativarMotoristaService',
    'ReativarMotoristaService',
    'ExcluirMotoristaService',
    'CadastrarVeiculoService',
    'AtualizarVeiculoService',
    'ExcluirVeiculoService',
    'VincularMotoristaVeiculoService',
    'ListarOcorrenciasService',
    'ObterDadosFormularioOcorrenciaService',
    'RegistrarOcorrenciaService',
    'AtualizarOcorrenciaService',
    'ObterDetalheOcorrenciaService',
    'BuscarOficinasParaOcorrenciaService',
    'EncerrarOcorrenciaService',
    'AtualizarStatusOcorrenciaService',
    'VincularOficinaOcorrenciaService',
    'ListarOficinasService',
    'ObterDetalheOficinaService',
    'FavoritarOficinaService',
    'GerarRelatorioService',
    'FiltrarRelatorioService',
    'GerarRelatorioCsvService',
    'ReabrirOcorrenciaService',
    'ObterPerfilService',
    'AtualizarPerfilService',
    'CadastrarOficinaService',
    'AtualizarOficinaService',
    'AlterarStatusOficinaService',
    'ListarMinhasOficinasService',
    'DefinirAcessoMotoristaService',
    'AutenticarMotoristaService',
    'TrocarSenhaMotoristaService',
    'ObterPainelMotoristaService',
    'ObterOcorrenciaMotoristaService',
    'buscar_ocorrencia_do_motorista',
    'buscar_oficinas_compativeis',
]
