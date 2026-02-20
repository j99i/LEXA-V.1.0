import uuid
from decimal import Decimal
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import FileExtensionValidator
from django.utils import timezone
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings

# ==========================================
# 1. USUARIOS
# ==========================================
class Usuario(AbstractUser):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    avatar = models.ImageField(upload_to='avatares/', null=True, blank=True)
    telefono = models.CharField(max_length=20, blank=True, null=True)
    puesto = models.CharField(max_length=100, blank=True, null=True)

    CHOICES_ROL = (
        ('admin', 'Administrador Master'),
        ('analista_sr', 'Abogado Senior'),
        ('analista_jr', 'Abogado Junior')
    )
    rol = models.CharField(max_length=20, choices=CHOICES_ROL, default='analista_jr', db_index=True)
    
    # Permisos
    can_create_client = models.BooleanField(default=False)
    can_edit_client = models.BooleanField(default=False)
    can_delete_client = models.BooleanField(default=False)
    can_view_documents = models.BooleanField(default=True)
    can_upload_files = models.BooleanField(default=False)
    can_manage_users = models.BooleanField(default=False)

    # Accesos
    access_finanzas = models.BooleanField(default=False)
    access_cotizaciones = models.BooleanField(default=False)
    access_contratos = models.BooleanField(default=False)
    access_disenador = models.BooleanField(default=False)
    access_agenda = models.BooleanField(default=False)
    access_gastos = models.BooleanField(default=False)   # NUEVO
    access_qr = models.BooleanField(default=False) 

    clientes_asignados = models.ManyToManyField('Cliente', blank=True, related_name='abogados_asignados')

    def save(self, *args, **kwargs):
        if self.rol == 'admin':
            self.is_staff = True
            self.is_superuser = True
            for field in ['can_create_client', 'can_edit_client', 'can_delete_client', 'can_upload_files', 'can_manage_users', 'access_finanzas', 'access_cotizaciones', 'access_contratos', 'access_disenador', 'access_agenda', 'access_gastos', 'access_qr']:
                setattr(self, field, True)
        super().save(*args, **kwargs)

# ==========================================
# 2. CLIENTES
# ==========================================
class Cliente(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    nombre_empresa = models.CharField(max_length=200, unique=True, db_index=True)
    nombre_contacto = models.CharField(max_length=200)
    telefono = models.CharField(max_length=20, blank=True)
    email = models.EmailField()
    
    # --- CAMPO NUEVO (Dirección) ---
    direccion = models.TextField(blank=True, null=True, verbose_name="Dirección Fiscal")
    
    logo = models.ImageField(upload_to='logos_clientes/', null=True, blank=True)
    fecha_registro = models.DateTimeField(auto_now_add=True)
    datos_extra = models.JSONField(default=dict, blank=True) 

    def __str__(self):
        return self.nombre_empresa

    # --- LÓGICA AUTOMÁTICA PARA EL PDF ---
    @property
    def direccion_completa(self):
        # 1. Si se llenó en el cliente, usar esa.
        if self.direccion:
            return self.direccion
        
        # 2. Si no, buscar en la cotización original.
        cotizacion_origen = self.cotizacion_origen.order_by('-fecha_creacion').first()
        if cotizacion_origen and cotizacion_origen.prospecto_direccion:
            return cotizacion_origen.prospecto_direccion
            
        return "Domicilio no especificado"

class CampoAdicional(models.Model):
    TIPOS = (('text', 'Texto Corto'), ('textarea', 'Texto Largo'), ('date', 'Fecha'), ('number', 'Número'))
    nombre = models.CharField(max_length=100)
    tipo = models.CharField(max_length=20, choices=TIPOS, default='text')
    obligatorio = models.BooleanField(default=False)

# ==========================================
# 3. DRIVE Y ARCHIVOS
# ==========================================
class Carpeta(models.Model):
    nombre = models.CharField(max_length=255, db_index=True)
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE, related_name='carpetas_drive')
    padre = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='subcarpetas')
    es_expediente = models.BooleanField(default=False)
    creada_el = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.nombre} - {self.cliente.nombre_empresa}"

    def obtener_detalle_cumplimiento(self):
        # --- DEFINICIÓN MAESTRA DE REQUISITOS (Basada en PDF del Cliente) ---
        requisitos = {
            'CARPETA ADMINISTRATIVA': [
                'ACTA CONSTITUTIVA', 'PODER NOTARIAL', 'IDENTIFICACIÓN DEL REPRESENTANTE LEGAL', 
                'CONSTANCIA DE SITUACIÓN FISCAL', 'PAGO PREDIAL', 'PAGO DE AGUA', 
                'PLANO', 'ACREDITACION DE PROPIEDAD O POSESIÓN'
            ],
            'LICENCIA DE FUNCIONAMIENTO': [
                'LICENCIA DE FUNCIONAMIENTO ANTERIOR', 'ACUSE DE INGRESO', 'ORDEN DE PAGO', 
                'RECIBO OFICIAL DE PAGO', 'FACTURA PAGO DE DERECHOS', 'COMPROBANTE DE APORTACIÓN', 
                'LICENCIA DE FUNCIONAMIENTO ACTUAL'
            ],
            'PROGRAMA ESPECIFICO DE PROTECCIÓN CIVIL': [
                'PEPC VIGENTE', 'DICTAMEN ESTRUCTURAL', 'DICTAMEN ELECTRICO', 'ALERTAMIENTO SISMICO', 
                'RESPONSIVA DE EXTINTORES', 'POLIZA DE SEGURO', 'CONSTANCIAS DE CAPACITACIÓN', 
                'CONSTANCIAS 1ER SIMULACRO', 'CONSTANCIAS 2DO SIMULACRO', 'CONSTANCIAS 3ER SIMULACRO'
            ],
            'PROTECCIÓN CIVIL MUNICIPAL': [
                'DICTAMEN ANTERIOR', 'ACUSE DE INGRESO', 'ORDEN DE PAGO', 'RECIBO OFICIAL DE PAGO', 
                'FACTURA PAGO DE DERECHOS', 'COMPROBANTE DE APORTACIÓN', 'DICTAMEN ACTUAL'
            ],
            'PROTECCIÓN CIVIL ESTATAL': [
                'REGISTRO ANTERIOR', 'ACUSE DE INGRESO', 'ORDEN DE PAGO', 'RECIBO OFICIAL DE PAGO', 
                'FACTURA PAGO DE DERECHOS', 'COMPROBANTE DE APORTACIÓN', 'REGISTRO ACTUAL'
            ],
            'MEDIO AMBIENTE': [
                'AUTORIZACIONES ANTERIORES', 'ACUSES DE INGRESO', 'ANALISIS DE AGUA RESIDUAL VIGENTE', 
                'ANALISIS DE EMISIONES VIGENTE', 'ORDEN DE PAGO', 'RECIBO OFICIAL DE PAGO', 
                'FACTURA PAGO DE DERECHOS', 'COMPROBANTE DE APORTACIÓN', 'VISTO BUENO ACTUAL', 
                'REGISTRO DE DESCARGA DE AGUAS RESIDUALES ACTUAL', 'LICENCIA DE EMISIONES A LA ATMOSFERA ACTUAL'
            ],
            'REGISTRO AMBIENTAL ESTATAL': [
                'AUTORIZACION ANTERIOR', 'ACUSES DE INGRESO', 'FACTURA DE RECOLECCIÓN DE BASURA', 
                'CONTRATO DE RECOLECCIÓN DE BASURA', 'REGISTRO DE RECOLECTOR DE BASURA', 'ORDEN DE PAGO', 
                'RECIBO OFICIAL DE PAGO', 'FACTURA PAGO DE DERECHOS', 'COMPROBANTE DE APORTACIÓN', 
                'AUTORIZACIÓN ACTUAL'
            ],
            'CEDULA DE ZONIFICACIÓN': [
                'REGISTRO ANTERIOR', 'ACUSE DE INGRESO', 'ORDEN DE PAGO', 'RECIBO OFICIAL DE PAGO', 
                'FACTURA PAGO DE DERECHOS', 'COMPROBANTE DE APORTACIÓN', 'REGISTRO ACTUAL'
            ],
            'LICENCIA DE USO DE SUELO': [
                'REGISTRO ANTERIOR', 'ACUSE DE INGRESO', 'ORDEN DE PAGO', 'RECIBO OFICIAL DE PAGO', 
                'FACTURA PAGO DE DERECHOS', 'COMPROBANTE DE APORTACIÓN', 'REGISTRO ACTUAL'
            ]
        }

        nombre_key = self.nombre.upper()
        if nombre_key not in requisitos:
            return None

        lista_req = requisitos[nombre_key]
        detalle = []
        for req in lista_req:
            # Busca archivos que contengan el nombre del requisito (flexible)
            doc = self.documentos.filter(nombre_archivo__icontains=req).order_by('-fecha_subida').first()
            
            if doc:
                detalle.append({'nombre': req, 'estado': 'ok', 'doc': doc})
            else:
                detalle.append({'nombre': req, 'estado': 'missing', 'doc': None})
        return detalle

class Archivo(models.Model):
    nombre = models.CharField(max_length=200)
    carpeta = models.ForeignKey(Carpeta, on_delete=models.CASCADE, related_name='archivos')
    archivo = models.FileField(upload_to='temp_uploads/') 
    subido_por = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    fecha_subida = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.nombre

class Expediente(models.Model):
    ESTADOS = (('abierto', 'Abierto'), ('pausado', 'En Pausa'), ('finalizado', 'Finalizado'))
    cliente = models.ForeignKey(Cliente, related_name='expedientes', on_delete=models.CASCADE)
    carpeta = models.OneToOneField(Carpeta, on_delete=models.CASCADE, null=True, blank=True)
    num_expediente = models.CharField(max_length=50, unique=True)
    titulo = models.CharField(max_length=200)
    descripcion = models.TextField(blank=True)
    estado = models.CharField(max_length=20, choices=ESTADOS, default='abierto')
    prioridad = models.IntegerField(choices=((1, 'Baja'), (2, 'Media'), (3, 'Crítica')), default=2)
    creado_el = models.DateTimeField(auto_now_add=True)

class Documento(models.Model):
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE, related_name='documentos')
    carpeta = models.ForeignKey(Carpeta, on_delete=models.CASCADE, related_name='documentos', null=True, blank=True)
    archivo = models.FileField(upload_to='drive_legal/%Y/%m/%d/')
    nombre_archivo = models.CharField(max_length=255)
    subido_por = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    fecha_subida = models.DateTimeField(auto_now_add=True)
    fecha_vencimiento = models.DateField(null=True, blank=True, verbose_name="Fecha de Vencimiento")

    def __str__(self):
        return self.nombre_archivo

    class Meta:
        verbose_name = "Documento"
        verbose_name_plural = "Documentos"
        ordering = ['-fecha_subida']

# ==========================================
# 4. GESTIÓN
# ==========================================
class Tarea(models.Model):
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE, related_name='tareas')
    titulo = models.CharField(max_length=255)
    fecha_limite = models.DateField()
    completada = models.BooleanField(default=False)
    prioridad = models.CharField(max_length=10, default='media')
    creada_el = models.DateTimeField(auto_now_add=True)

class Bitacora(models.Model):
    usuario = models.ForeignKey(Usuario, on_delete=models.SET_NULL, null=True)
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE)
    accion = models.CharField(max_length=50)
    descripcion = models.TextField()
    fecha = models.DateTimeField(auto_now_add=True)

class Plantilla(models.Model):
    nombre = models.CharField(max_length=100)
    archivo = models.FileField(upload_to='plantillas_word/', validators=[FileExtensionValidator(allowed_extensions=['docx'])])
    fecha_subida = models.DateTimeField(auto_now_add=True)

class VariableEstandar(models.Model):
    clave = models.CharField(max_length=100, unique=True)
    descripcion = models.CharField(max_length=255)
    tipo = models.CharField(max_length=20, default='texto')
    origen = models.CharField(max_length=20, default='usuario')
    campo_bd = models.CharField(max_length=100, blank=True, null=True)

# ==========================================
# 5. COTIZACIONES
# ==========================================
class Servicio(models.Model):
    nombre = models.CharField(max_length=200)
    descripcion = models.TextField(blank=True, null=True)
    precio_base = models.DecimalField(max_digits=10, decimal_places=2)
    campos_dinamicos = models.JSONField(default=dict, blank=True)

    def __str__(self):
        return self.nombre

class PlantillaMensaje(models.Model):
    TIPOS = (('email', 'Correo'), ('whatsapp', 'WhatsApp'))
    tipo = models.CharField(max_length=20, choices=TIPOS)
    asunto = models.CharField(max_length=200, blank=True)
    cuerpo = models.TextField()
    imagen_cabecera = models.ImageField(upload_to='plantillas_img/', blank=True, null=True)

class Cotizacion(models.Model):
    ESTADOS = (
        ('borrador', 'Borrador'),
        ('enviada', 'Enviada'),
        ('aceptada', 'Aceptada'),
        ('rechazada', 'Rechazada'),
    )

    folio = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    titulo = models.CharField(max_length=255, verbose_name="Título del Proyecto", blank=True, null=True, help_text="Ej. Renovación de Licencias 2026")
    
    # Datos del Cliente
    prospecto_empresa = models.CharField(max_length=200, blank=True, null=True, verbose_name="Empresa")
    prospecto_nombre = models.CharField(max_length=200, verbose_name="Nombre del Contacto")
    prospecto_email = models.EmailField(blank=True, null=True)
    prospecto_telefono = models.CharField(max_length=20, blank=True, null=True)
    prospecto_direccion = models.TextField(verbose_name="Dirección Fiscal Completa", blank=True, null=True)
    prospecto_cargo = models.CharField(max_length=150, verbose_name="Cargo", blank=True, null=True)
    
    # Lógica de Descuento
    porcentaje_descuento = models.DecimalField(max_digits=5, decimal_places=2, default=0.00, verbose_name="Descuento (%)")
    descuento = models.DecimalField(max_digits=12, decimal_places=2, default=0.00, verbose_name="Descuento ($)")

    # IVA Flexible
    aplica_iva = models.BooleanField(default=False, verbose_name="¿Lleva IVA?")
    porcentaje_iva = models.DecimalField(max_digits=5, decimal_places=2, default=16.00, verbose_name="Tasa IVA (%)")
    monto_iva = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)

    # Totales
    subtotal = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    total = models.DecimalField(max_digits=12, decimal_places=2, default=0.00) # Neto sin IVA
    total_con_iva = models.DecimalField(max_digits=12, decimal_places=2, default=0.00) # Total Final
    
    # Metadatos
    creado_por = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    validez_hasta = models.DateField(null=True, blank=True)
    estado = models.CharField(max_length=20, choices=ESTADOS, default='borrador')
    
    cliente_convertido = models.ForeignKey('Cliente', on_delete=models.SET_NULL, null=True, blank=True, related_name='cotizacion_origen')
    
    # Condiciones Comerciales
    OPCIONES_PAGO = (
        ('50_50', '50% Anticipo - 50% al Finalizar'),
        ('100_entrega', '100% Contra Entrega de Resultados'),
        ('contado', 'Pago de Contado (Una sola exhibición)')
    )
    condiciones_pago = models.CharField(max_length=20, choices=OPCIONES_PAGO, default='50_50', verbose_name="Forma de Pago")

    OPCIONES_TIEMPO = (
        ('30_dias', '30 Días Hábiles'),
        ('60_dias', '60 Días Hábiles'),
        ('90_dias', '90 Días Hábiles'),
        ('indefinido', 'Por definir según avance procesal')
    )
    tiempo_entrega = models.CharField(max_length=20, choices=OPCIONES_TIEMPO, default='30_dias', verbose_name="Tiempo de Gestión")

    def __str__(self):
        return f"Cotización #{self.id} - {self.prospecto_empresa or self.prospecto_nombre}"

    def calcular_totales(self):
        suma_items = sum(item.cantidad * item.precio_unitario for item in self.items.all())
        self.subtotal = Decimal(suma_items)
        
        if self.porcentaje_descuento > 0:
            self.descuento = self.subtotal * (self.porcentaje_descuento / Decimal('100'))
        else:
            self.descuento = Decimal('0.00')
            
        base_imponible = self.subtotal - self.descuento

        if self.aplica_iva:
            self.monto_iva = base_imponible * (self.porcentaje_iva / Decimal('100'))
        else:
            self.monto_iva = Decimal('0.00')

        self.total = base_imponible
        self.total_con_iva = base_imponible + self.monto_iva
        
        Cotizacion.objects.filter(id=self.id).update(
            subtotal=self.subtotal,
            descuento=self.descuento,
            aplica_iva=self.aplica_iva,
            porcentaje_iva=self.porcentaje_iva,
            monto_iva=self.monto_iva,
            total=self.total,
            total_con_iva=self.total_con_iva
        )

class ItemCotizacion(models.Model):
    cotizacion = models.ForeignKey(Cotizacion, related_name='items', on_delete=models.CASCADE)
    servicio = models.ForeignKey(Servicio, on_delete=models.CASCADE)
    cantidad = models.PositiveIntegerField(default=1)
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2)
    subtotal = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    descripcion_personalizada = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.servicio.nombre} x {self.cantidad}"

    def save(self, *args, **kwargs):
        self.subtotal = Decimal(self.cantidad) * Decimal(self.precio_unitario)
        super().save(*args, **kwargs)
        self.cotizacion.calcular_totales()

# ==========================================
# 6. FINANZAS
# ==========================================
class CuentaPorCobrar(models.Model):
    ESTADOS = (('pendiente', 'Pendiente'), ('parcial', 'Parcial'), ('pagado', 'Pagado'))
    cliente = models.ForeignKey(Cliente, related_name='cuentas', on_delete=models.CASCADE)
    cotizacion = models.ForeignKey(Cotizacion, on_delete=models.CASCADE, related_name='pagos_programados', null=True, blank=True)
    concepto = models.CharField(max_length=200)
    monto_total = models.DecimalField(max_digits=12, decimal_places=2)
    monto_pagado = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    saldo_pendiente = models.DecimalField(max_digits=12, decimal_places=2)
    fecha_emision = models.DateTimeField(auto_now_add=True)
    fecha_vencimiento = models.DateField(null=True, blank=True, db_index=True)
    estado = models.CharField(max_length=20, choices=ESTADOS, default='pendiente', db_index=True)

    def save(self, *args, **kwargs):
        self.saldo_pendiente = self.monto_total - self.monto_pagado
        self.estado = 'pagado' if self.saldo_pendiente <= 0 else ('parcial' if self.monto_pagado > 0 else 'pendiente')
        super().save(*args, **kwargs)

class Pago(models.Model):
    METODOS = (('transferencia', 'Transferencia'), ('efectivo', 'Efectivo'), ('tarjeta', 'Tarjeta'), ('cheque', 'Cheque'))
    cuenta = models.ForeignKey(CuentaPorCobrar, related_name='pagos', on_delete=models.CASCADE)
    monto = models.DecimalField(max_digits=12, decimal_places=2)
    fecha_pago = models.DateField(default=timezone.now)
    metodo = models.CharField(max_length=20, choices=METODOS)
    referencia = models.CharField(max_length=100, blank=True)
    comprobante = models.FileField(upload_to='comprobantes_pago/', null=True, blank=True)
    registrado_por = models.ForeignKey(Usuario, on_delete=models.SET_NULL, null=True)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.cuenta.monto_pagado = sum(p.monto for p in self.cuenta.pagos.all())
        self.cuenta.save()

# ==========================================
# 7. AGENDA
# ==========================================
class Evento(models.Model):
    TIPOS = (('audiencia', 'Audiencia'), ('vencimiento', 'Vencimiento'), ('reunion', 'Reunión'), ('tramite', 'Trámite'), ('personal', 'Personal'))
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE, null=True, blank=True, related_name='eventos')
    titulo = models.CharField(max_length=200)
    inicio = models.DateTimeField(db_index=True)
    fin = models.DateTimeField(null=True, blank=True)
    tipo = models.CharField(max_length=20, choices=TIPOS, default='reunion')
    descripcion = models.TextField(blank=True)
    completado = models.BooleanField(default=False)

    @property
    def color_hex(self):
        colores = {'audiencia': '#ef4444', 'vencimiento': '#f59e0b', 'reunion': '#3b82f6', 'tramite': '#10b981', 'personal': '#6b7280'}
        return colores.get(self.tipo, '#3b82f6')

# ==========================================
# 8. SIGNALS (AUTOMATIZACIÓN DE CARPETAS)
# ==========================================
@receiver(post_save, sender=Cliente)
def crear_carpetas_base(sender, instance, created, **kwargs):
    if created:
        carpetas_nombres = [
            'CARPETA ADMINISTRATIVA', 
            'LICENCIA DE FUNCIONAMIENTO', 
            'PROGRAMA ESPECIFICO DE PROTECCIÓN CIVIL', 
            'PROTECCIÓN CIVIL MUNICIPAL', 
            'PROTECCIÓN CIVIL ESTATAL', 
            'MEDIO AMBIENTE', 
            'REGISTRO AMBIENTAL ESTATAL', 
            'CEDULA DE ZONIFICACIÓN', 
            'LICENCIA DE USO DE SUELO',
            'Cotizaciones' # Carpeta del sistema
        ]
        for nombre in carpetas_nombres:
            carpeta_padre, _ = Carpeta.objects.get_or_create(
                nombre=nombre,
                cliente=instance,
                defaults={'es_expediente': False}
            )
            
            # --- CREACIÓN AUTOMÁTICA DE SUB-CARPETA DE ENTREGA ---
            # Si la carpeta es una de las principales (tiene requisitos),
            # le creamos su subcarpeta para entregar el documento final.
            if nombre != 'CARPETA ADMINISTRATIVA' and nombre != 'Cotizaciones':
                Carpeta.objects.get_or_create(
                    nombre="Autorizaciones liberadas",
                    cliente=instance,
                    padre=carpeta_padre,
                    defaults={'es_expediente': False}
                )

# ==========================================
# 9. CARGA EXTERNA (CLIENT PORTAL)
# ==========================================
class SolicitudEnlace(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE, related_name='solicitudes_externas')
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    activa = models.BooleanField(default=True)

    def __str__(self):
        return f"Link para {self.cliente.nombre_empresa} ({self.id})"

class ArchivoTemporal(models.Model):
    solicitud = models.ForeignKey(SolicitudEnlace, on_delete=models.CASCADE, related_name='archivos_temp')
    archivo = models.FileField(upload_to='uploads_pendientes/')
    nombre_requisito = models.CharField(max_length=255)
    fecha_subida = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.nombre_requisito} - Pendiente"

# expedientes/models.py

class FacturaGasto(models.Model):
    # Identificador único del SAT (UUID) para evitar duplicados
    uuid = models.CharField(max_length=36, unique=True, verbose_name="Folio Fiscal (UUID)")
    
    # Datos del XML
    fecha_emision = models.DateTimeField()
    rfc_emisor = models.CharField(max_length=13)
    nombre_emisor = models.CharField(max_length=255)
    rfc_receptor = models.CharField(max_length=13)
    nombre_receptor = models.CharField(max_length=255)
    
    # Montos
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)
    total_impuestos = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total = models.DecimalField(max_digits=10, decimal_places=2)
    moneda = models.CharField(max_length=10, default="MXN")
    
    # Archivo físico
    archivo_xml = models.FileField(upload_to='gastos/xml/%Y/%m/')
    
    # Metadatos internos
    fecha_carga = models.DateTimeField(auto_now_add=True)
    cargado_por = models.ForeignKey(Usuario, on_delete=models.SET_NULL, null=True)
    
    def __str__(self):
        return f"{self.nombre_emisor} - ${self.total} ({self.fecha_emision.date()})"

    class Meta:
        verbose_name = "Gasto / Factura"
        verbose_name_plural = "Gastos y Facturas"
        ordering = ['-fecha_emision']