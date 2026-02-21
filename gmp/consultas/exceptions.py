from gmp.consultas.constants import (
    MSG_ERRO_AGENDAMENTO_FINALIZADO_DELETE,
    MSG_ERRO_CONSULTA_NAO_PODE_SER_DELETADA,
)



class ConsultaError(Exception):
    """
    Exceção base para erros relacionados ao domínio de consultas.
    """
    default_message = "Ocorreu um erro relacionado à consulta."

    def __init__(self, message=None):
        self.message = message or self.default_message
        super().__init__(self.message)

    def __str__(self):
        return self.message


class ConsultaStatusInvalidoError(ConsultaError):
    default_message = "Esta consulta não permite esta operação."


class ConsultaNaoMarcadaError(ConsultaError):
    default_message = "A consulta não está marcada."


class ConsultaNaoRealizadaError(ConsultaError):
    default_message = "A consulta ainda não foi realizada."


class ConsultaJaCanceladaError(ConsultaError):
    default_message = "A consulta já foi cancelada."


class ConsultaPassadaError(ConsultaError):
    default_message = "Não é possível realizar esta operação em consulta passada."


class ConsultaPermissaoNegadaError(ConsultaError):
    default_message = "Você não tem permissão para realizar esta ação."


class AntecedenciaInsuficienteError(ConsultaError):
    default_message = "A consulta deve respeitar a antecedência mínima permitida."


class HorarioIndisponivelError(ConsultaError):
    default_message = "O horário selecionado não está disponível."


class DadosReceitaInvalidosError(ConsultaError):
    default_message = "Os dados da receita são inválidos ou incompletos."


class ConsultaNaoEncontradaError(ConsultaError):
    default_message = "Consulta não encontrada."