from django.utils import timezone
from datetime import timedelta
from django.db.models import Q, Count
from .models import Tarea, Evento, CuentaPorCobrar, Cliente, ArchivoTemporal

def notificaciones_globales(request):
    if not request.user.is_authenticated:
        return {}

    hoy = timezone.now().date()
    
    # 1. Definir qué clientes puede ver este usuario
    if request.user.rol == 'admin':
        mis_clientes = Cliente.objects.all()
    else:
        mis_clientes = request.user.clientes_asignados.all()

    # 2. Buscar Recordatorios
    
    # A. Tareas Vencidas o de Hoy
    tareas = Tarea.objects.filter(
        cliente__in=mis_clientes, 
        completada=False, 
        fecha_limite__lte=hoy
    ).select_related('cliente').order_by('fecha_limite')

    # B. Eventos (Hoy y Mañana)
    mañana = hoy + timedelta(days=1)
    eventos = Evento.objects.filter(
        inicio__date__range=[hoy, mañana]
    ).filter(
        Q(usuario=request.user) | Q(cliente__in=mis_clientes)
    ).select_related('cliente').order_by('inicio')

    # C. Cobranza (Próximos 3 días) - Solo si tiene permiso
    cobros = []
    if request.user.rol == 'admin' or request.user.access_finanzas:
        cobros = CuentaPorCobrar.objects.filter(
            cliente__in=mis_clientes, 
            estado__in=['pendiente', 'parcial'],
            fecha_vencimiento__lte=hoy + timedelta(days=3)
        ).select_related('cliente')

    # D. NUEVO: Auditorías de Documentos (Archivos Temporales)
    # Agrupamos por cliente para que si suben 10 archivos, salga 1 sola notificación con el conteo.
    auditorias = ArchivoTemporal.objects.filter(
        solicitud__cliente__in=mis_clientes
    ).values(
        'solicitud__cliente__id', 
        'solicitud__cliente__nombre_empresa'
    ).annotate(
        total_archivos=Count('id')
    )

    # Conteo Total para el "Globito Rojo"
    total_notif = tareas.count() + eventos.count() + len(cobros) + len(auditorias)

    return {
        'notif_tareas': tareas,
        'notif_eventos': eventos,
        'notif_cobros': cobros,
        'notif_auditorias': auditorias, # <-- Lo pasamos al HTML
        'total_notif': total_notif
    }