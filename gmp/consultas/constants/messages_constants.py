# =========================
# SUCESSO
# =========================

MSG_CONSULTA_MARCADA_SUCESSO = "Consulta marcada com sucesso."
MSG_CONSULTA_CANCELADA_SUCESSO = "Consulta cancelada com sucesso."
MSG_CONSULTA_REGISTRADA_SUCESSO = "Consulta registrada com sucesso."
MSG_RECEITA_GERADA_SUCESSO = "Receita gerada com sucesso."


# =========================
# ERROS
# =========================

MSG_ERRO_SELECIONAR_PACIENTE = "Selecione um paciente."
MSG_ERRO_CONSULTA_JA_PROCESSADA = "Consulta já registrada ou cancelada."
MSG_ERRO_NAO_PODE_CANCELAR_PASSADA = "Não é possível cancelar consultas passadas."
MSG_ERRO_SEM_PERMISSAO = "Você não tem permissão para realizar esta ação."
MSG_ERRO_RECEITA_NAO_PERMITIDA = "Esta consulta não permite gerar receita."
MSG_ERRO_CRM_DESCRICAO_OBRIGATORIOS = "CRM e descrição são obrigatórios."
MSG_ERRO_MEDICO_NAO_PODE_MARCAR = "Médicos não podem marcar consultas."
MSG_ERRO_PREENCHER_TODOS_CAMPOS = "Preencha todos os campos."
MSG_ERRO_FINAL_DE_SEMANA = "Consultas não são permitidas aos finais de semana."
MSG_ERRO_LIMITE_DIARIO_MEDICO = "Este médico atingiu o limite de consultas para este dia."
MSG_ERRO_JA_POSSUI_CONSULTA_FUTURA = "Você já possui uma consulta futura marcada."
MSG_ERRO_ANTECEDENCIA_MINIMA = "Horário inválido. Escolha um horário futuro com pelo menos {horas} horas de antecedência."
MSG_ERRO_HORARIO_OCUPADO = "Este horário já está ocupado."
MSG_ERRO_JA_POSSUI_CONSULTA_NO_HORARIO = "Você já possui uma consulta marcada neste horário."
MSG_ERRO_AGENDAMENTO_FINALIZADO_DELETE = "Agendamento finalizado não pode ser deletado."
MSG_ERRO_CONSULTA_NAO_PODE_SER_DELETADA = "Consulta não pode ser deletada."


# =========================
# INFORMAÇÕES
# =========================

MSG_INFO_SEM_CONSULTAS_FILTRO = "Não há consultas registradas com estes parâmetros."
MSG_INFO_SEM_PACIENTES_QUEIXA = "Nenhum paciente encontrado com essa queixa."


# =========================
# EMAILS
# =========================

EMAIL_ASSUNTO_CONSULTA_CONFIRMADA = "Consulta confirmada"
EMAIL_MENSAGEM_CONSULTA_CONFIRMADA = (
    "Sua consulta foi marcada para {data_hora} "
    "com o médico {medico}."
)