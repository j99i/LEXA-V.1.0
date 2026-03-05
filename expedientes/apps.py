from django.apps import AppConfig
import threading
import time

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

        # SOLUCIÓN: Ejecutar el scheduler en un hilo separado con un retraso
        # para evitar el RuntimeWarning y que Gunicorn se bloquee.
        def start_scheduler_delayed():
            time.sleep(3)  # Espera 3 segundos a que Django cargue por completo
            try:
                from . import scheduler
                scheduler.start()
            except Exception as e:
                print(f"Error al iniciar scheduler: {e}")

        # Iniciar el hilo solo si no estamos en un entorno donde ya falló
        hilo = threading.Thread(target=start_scheduler_delayed)
        hilo.daemon = True # El hilo muere si la app se apaga
        hilo.start()