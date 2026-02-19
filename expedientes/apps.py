from django.apps import AppConfig

class ExpedientesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'expedientes'

    def ready(self):
        import os
        # No iniciar en comandos de manage.py como migrate, collectstatic, etc.
        if os.environ.get('RUN_MAIN') != 'true' and os.environ.get('DJANGO_SETTINGS_MODULE'):
            try:
                from . import scheduler
                scheduler.start()
            except Exception:
                # La tabla aún no existe (primer migrate), se ignora
                pass