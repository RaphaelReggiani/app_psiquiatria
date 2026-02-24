from gmp.consultas.constants.messages_constants import (
    MSG_ERRO_ANTECEDENCIA_MINIMA,
    MSG_ERRO_CONSULTA,
    MSG_ERRO_CONSULTA_JA_CANCELADA,
    MSG_ERRO_CONSULTA_NAO_ENCONTRADA,
    MSG_ERRO_CONSULTA_NAO_MARCADA,
    MSG_ERRO_CONSULTA_NAO_REALIZADA,
    MSG_ERRO_CRM_DESCRICAO_OBRIGATORIOS,
    MSG_ERRO_HORARIO_OCUPADO,
    MSG_ERRO_NAO_PODE_CANCELAR_PASSADA,
    MSG_ERRO_SEM_PERMISSAO,
    MSG_ERRO_STATUS_INVALIDO,
)


class ConsultaError(Exception):

    default_message = MSG_ERRO_CONSULTA

    def __init__(self, message=None):
        self.message = message or self.default_message
        super().__init__(self.message)

    def __str__(self):
        return self.message


class ConsultaStatusInvalidoError(ConsultaError):
    default_message = MSG_ERRO_STATUS_INVALIDO


class ConsultaNaoMarcadaError(ConsultaError):
    default_message = MSG_ERRO_CONSULTA_NAO_MARCADA


class ConsultaNaoRealizadaError(ConsultaError):
    default_message = MSG_ERRO_CONSULTA_NAO_REALIZADA


class ConsultaJaCanceladaError(ConsultaError):
    default_message = MSG_ERRO_CONSULTA_JA_CANCELADA


class ConsultaPassadaError(ConsultaError):
    default_message = MSG_ERRO_NAO_PODE_CANCELAR_PASSADA


class ConsultaPermissaoNegadaError(ConsultaError):
    default_message = MSG_ERRO_SEM_PERMISSAO


class AntecedenciaInsuficienteError(ConsultaError):
    default_message = MSG_ERRO_ANTECEDENCIA_MINIMA


class HorarioIndisponivelError(ConsultaError):
    default_message = MSG_ERRO_HORARIO_OCUPADO


class DadosReceitaInvalidosError(ConsultaError):
    default_message = MSG_ERRO_CRM_DESCRICAO_OBRIGATORIOS


class ConsultaNaoEncontradaError(ConsultaError):
    default_message = MSG_ERRO_CONSULTA_NAO_ENCONTRADA
