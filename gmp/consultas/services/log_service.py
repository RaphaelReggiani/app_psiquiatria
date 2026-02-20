from gmp.consultas.models import ConsultaLog


def registrar_log(consulta, usuario, status_anterior, status_novo):
    ConsultaLog.objects.create(
        consulta=consulta,
        usuario=usuario,
        status_anterior=status_anterior,
        status_novo=status_novo
    )