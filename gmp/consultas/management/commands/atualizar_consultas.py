from django.core.management.base import BaseCommand

from gmp.consultas.models import AgendamentoConsulta


class Command(BaseCommand):
    help = "Atualiza consultas expiradas"

    def handle(self, *args, **kwargs):
        total = AgendamentoConsulta.atualizar_consultas_expiradas()
        self.stdout.write(self.style.SUCCESS(f"{total} consultas atualizadas."))
