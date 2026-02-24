# =========================
# API MESSAGES
# =========================

API_ERROR_CONSULTA_UPDATE_NOT_ALLOWED = "consulta_update_not_allowed"
API_ERROR_MEDICO_NAO_PODE_MARCAR = "medico_nao_pode_marcar"
API_ERROR_SEM_PERMISSAO = "permission_denied"

# =========================
# API ERROR MESSAGES
# =========================

API_ERROR_AGENDAMENTO_FINALIZADO = "Agendamento finalizado não pode ser alterado."
API_ERROR_STATUS_PERMISSION = "Você não pode alterar o status."
API_ERROR_OUTRO_MEDICO = "Você não pode alterar agendamento de outro médico."
API_ERROR_AGENDAMENTO_PASSADO = (
    "Não é permitido criar consulta para agendamento no passado."
)
API_ERROR_CONSULTA_EXISTENTE = "Este agendamento já possui consulta registrada."
API_ERROR_APENAS_MEDICO = "Apenas médicos podem registrar consultas."
API_ERROR_CONSULTA_OUTRO_MEDICO = "Você não pode registrar consulta de outro médico."
API_ERROR_STATUS_NAO_REALIZADO = (
    "Consulta só pode ser registrada para agendamento realizado."
)
API_ERROR_ARQUIVO_MAX_SIZE = "Arquivo excede o tamanho máximo de 6MB."
API_ERROR_ARQUIVO_NAO_PDF = "A receita deve ser PDF."
API_ERROR_ARQUIVO_TIPO_INVALIDO = "Tipo inválido."
