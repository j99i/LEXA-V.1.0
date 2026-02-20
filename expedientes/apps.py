from django.apps import AppConfig


class ExpedientesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'expedientes'

    def ready(self):
        import os
        import sys

        # Comandos de manage.py donde NO debe arrancar el scheduler
        comandos_excluidos = [
            'migrate',
            'makemigrations',
            'collectstatic',
            'createsuperuser',
            'shell',
            'test',
            'check',
        ]

        # Si se está corriendo un comando de manage.py excluido, salir sin arrancar
        if any(cmd in sys.argv for cmd in comandos_excluidos):
            return

        try:
            from . import scheduler
            scheduler.start()
        except Exception:
            # La tabla aún no existe (primer migrate) o cualquier otro error, se ignora
            pass