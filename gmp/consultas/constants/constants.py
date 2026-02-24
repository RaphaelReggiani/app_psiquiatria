# =========================
# URLS
# =========================

URL_MARCAR_CONSULTA = "marcar_consulta"
URL_AGENDA_MEDICO = "agenda_medico"
URL_MINHAS_CONSULTAS = "minhas_consultas"
URL_HISTORICO_PACIENTE = "historico_paciente"
URL_CADASTRAR_CONSULTA = "cadastrar_consulta"
URL_HORARIOS_DISPONIVEIS = "horarios_disponiveis"
URL_CANCELAR_CONSULTA = "cancelar_consulta"
URL_HISTORICO_MEDICO_CONSULTAS = "historico_medico_consultas"
URL_MEDICO_PACIENTES = "medico_pacientes"
URL_VISUALIZAR_RECEITA = "visualizar_receita"
URL_GERAR_RECEITA_PREVIEW = "gerar_receita_preview"

# =========================
# INPUTS
# =========================

LIMITE_DIARIO_MEDICO = 9
ANTECEDENCIA_MINIMA_HORAS = 2
DIA_UTIL_FINAL = 4
HORA_INICIO_ATENDIMENTO = 8
HORA_FIM_ATENDIMENTO = 21
FORMATO_HORA = "%H:%M"
FORMATO_DATA = "%Y-%m-%d"
INTERVALO_MINUTOS = (0, 30)

# =========================
# LOG / CACHE
# =========================

CACHE_TIMEOUT_HORARIOS = 60
LOG_STATUS_INICIAL = "-"

# =========================
# PAGINAÇÃO
# =========================

PAGINACAO_PADRAO = 10

# =========================
# LABELS
# =========================

LABEL_CONDICAO_PACIENTE = "Condição do Paciente"
LABEL_DESCRICAO_CONSULTA = "Descrição da Consulta"
LABEL_RECEITA = "Receita"
LABEL_ARQUIVO = "Arquivo"
LABEL_SELECIONE_MEDICO = "Selecione o médico"
LABEL_DATA_DA_CONSULTA = "Data da Consulta"
LABEL_HORARIO = "Horário"

# =========================
# STATUS
# =========================

STATUS_INICIAL = "inicial"
STATUS_MARCADA = "marcada"
STATUS_REALIZADA = "realizada"
STATUS_CANCELADA = "cancelada"
STATUS_NAO_REALIZADA = "nao_realizada"
STATUS_RECEITA_GERADA = "receita_gerada"

# =========================
# STATUS LABELS
# =========================

STATUS_LABEL_INICIAL = "Inicial"
STATUS_LABEL_MARCADA = "Marcada"
STATUS_LABEL_REALIZADA = "Realizada"
STATUS_LABEL_CANCELADA = "Cancelada"
STATUS_LABEL_NAO_REALIZADA = "Não Realizada"
STATUS_LABEL_RECEITA_GERADA = "Receita Gerada"
STATUS_LABEL_CONDICAO_PACIENTE_ESTAVEL = "Estável"
STATUS_LABEL_CONDICAO_PACIENTE_INSTAVEL = "Instável"
STATUS_LABEL_CONDICAO_PACIENTE_CRITICA = "Crítica"
