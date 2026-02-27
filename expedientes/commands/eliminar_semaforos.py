from django.core.management.base import BaseCommand
from expedientes.models import Carpeta

class Command(BaseCommand):
    help = 'Elimina todas las carpetas con semáforo de todos los clientes'

    def add_arguments(self, parser):
        # Este argumento nos protege de borrar cosas por accidente
        parser.add_argument(
            '--confirmar',
            action='store_true',
            help='Ejecuta el borrado real. Sin esto, solo muestra qué se va a borrar.',
        )

    def handle(self, *args, **options):
        # Lista exacta de las carpetas que tienen semáforo en tu sistema
        nombres_semaforo = [
            'Autorizaciones liberadas',
            'CARPETA ADMINISTRATIVA',
            'LICENCIA DE FUNCIONAMIENTO',
            'PROGRAMA ESPECIFICO DE PROTECCIÓN CIVIL',
            'PROTECCIÓN CIVIL MUNICIPAL',
            'PROTECCIÓN CIVIL ESTATAL',
            'MEDIO AMBIENTE',
            'REGISTRO AMBIENTAL ESTATAL',
            'CEDULA DE ZONIFICACIÓN',
            'LICENCIA DE USO DE SUELO'
        ]
        
        carpetas = Carpeta.objects.filter(nombre__in=nombres_semaforo)
        total = carpetas.count()
        
        self.stdout.write(self.style.WARNING(f'Buscando carpetas con semáforo... Se encontraron {total}.'))
        
        if total == 0:
            self.stdout.write(self.style.SUCCESS('No hay carpetas con semáforo para borrar.'))
            return

        if options['confirmar']:
            self.stdout.write('Borrando carpetas y sus archivos en S3 (esto puede tardar unos segundos)...')
            # Iteramos una por una para asegurar que si hay archivos en Amazon S3, 
            # se disparen las señales (signals) de borrado correctamente.
            for c in carpetas:
                c.delete()
            self.stdout.write(self.style.SUCCESS(f'¡Éxito! Se han eliminado {total} carpetas con semáforo definitivamente.'))
        else:
            self.stdout.write('--- MODO PRUEBA (No se ha borrado nada aún) ---')
            for c in carpetas[:15]:
                self.stdout.write(f"- {c.cliente.nombre_empresa} -> {c.nombre}")
            if total > 15:
                self.stdout.write(f"... y {total - 15} carpetas más.")
            
            self.stdout.write(self.style.ERROR('\nPara borrar DE VERDAD, ejecuta el comando agregando la bandera --confirmar'))