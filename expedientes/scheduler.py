import os
import subprocess
from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler
from django_apscheduler.jobstores import DjangoJobStore
import cloudinary.uploader
import logging

logger = logging.getLogger(__name__)

def hacer_backup_db():
    """
    Exporta la base de datos PostgreSQL y la sube a Cloudinary.
    Se ejecuta automáticamente cada noche a las 2am.
    """
    try:
        fecha = datetime.now().strftime('%Y-%m-%d_%H-%M')
        nombre = f"backup_{fecha}.sql"
        ruta_local = f"/tmp/{nombre}"

        # Exportar la DB usando pg_dump
        db_url = os.environ.get('DATABASE_URL')
        subprocess.run(
            ['pg_dump', db_url, '-f', ruta_local],
            check=True,
            capture_output=True
        )

        # Subir a Cloudinary como archivo raw
        cloudinary.uploader.upload(
            ruta_local,
            resource_type='raw',
            public_id=f"backups/{nombre}",
            overwrite=True
        )

        # Limpiar archivo temporal
        os.remove(ruta_local)
        logger.info(f"✅ Backup completado: {nombre}")

    except Exception as e:
        logger.error(f"❌ Error en backup: {e}")


def start():
    scheduler = BackgroundScheduler()
    scheduler.add_jobstore(DjangoJobStore(), "default")

    scheduler.add_job(
        hacer_backup_db,
        'cron',
        hour=8,        # 2am México = 8am UTC
        minute=0,
        id='backup_diario',
        replace_existing=True,
    )

    scheduler.start()
    logger.info("Scheduler de backups iniciado.")