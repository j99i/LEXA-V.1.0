from django.contrib import admin
from django.urls import path, re_path
from django.conf import settings
from django.views.static import serve
from django.contrib.auth import views as auth_views
from django.conf.urls.static import static  # <-- IMPORTACIÓN NUEVA AÑADIDA
from expedientes import views

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # AUTH
    path('login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    path('logout/', views.signout, name='logout'),
    path('registro/', views.registro, name='registro'),
    path('perfil/', views.mi_perfil, name='mi_perfil'),
    path('reset_password/', auth_views.PasswordResetView.as_view(template_name="registration/password_reset.html"), name='password_reset'),
    path('reset_password_sent/', auth_views.PasswordResetDoneView.as_view(template_name="registration/password_reset_done.html"), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name="registration/password_reset_confirm.html"), name='password_reset_confirm'),
    path('reset_password_complete/', auth_views.PasswordResetCompleteView.as_view(template_name="registration/password_reset_complete.html"), name='password_reset_complete'),

    # CORE
    path('', views.dashboard, name='dashboard'),
    path('usuarios/', views.gestion_usuarios, name='gestion_usuarios'),
    path('usuarios/autorizar/<uuid:user_id>/', views.autorizar_usuario, name='autorizar_usuario'),
    path('usuarios/editar/<uuid:user_id>/', views.editar_usuario, name='editar_usuario'),
    path('usuarios/eliminar/<uuid:user_id>/', views.eliminar_usuario, name='eliminar_usuario'),
    
    path('cliente/nuevo/', views.nuevo_cliente, name='nuevo_cliente'),
    path('cliente/eliminar/<uuid:cliente_id>/', views.eliminar_cliente, name='eliminar_cliente'),
    path('cliente/<uuid:cliente_id>/', views.detalle_cliente, name='detalle_cliente'),
    path('cliente/<uuid:cliente_id>/carpeta/<int:carpeta_id>/', views.detalle_cliente, name='detalle_carpeta'),
    path('cliente/editar/<uuid:cliente_id>/', views.editar_cliente, name='editar_cliente'),
    path('finanzas/eliminar/<int:id>/', views.eliminar_finanza, name='eliminar_finanza'),
    
    # CONFIGURACIÓN
    path('configuracion/campos/', views.configurar_campos, name='configurar_campos'),
    path('configuracion/campos/eliminar/<int:campo_id>/', views.eliminar_campo_dinamico, name='eliminar_campo_dinamico'),
    path('finanzas/cliente/<uuid:cliente_id>/', views.finanzas_cliente, name='finanzas_cliente'),
    
    # DRIVE
    path('carpeta/crear/<uuid:cliente_id>/', views.crear_carpeta, name='crear_carpeta'),
    path('carpeta/eliminar/<int:carpeta_id>/', views.eliminar_carpeta, name='eliminar_carpeta'),
    path('expediente/crear/<uuid:cliente_id>/', views.crear_expediente, name='crear_expediente'),
    path('archivo/subir/<uuid:cliente_id>/', views.subir_archivo_drive, name='subir_archivo_drive'),
    path('archivo/eliminar/<int:archivo_id>/', views.eliminar_archivo_drive, name='eliminar_archivo_drive'),
    path('drive/subir-requisito/<int:carpeta_id>/', views.subir_archivo_requisito, name='subir_archivo_requisito'),
    path('drive/zip/<int:carpeta_id>/', views.descargar_carpeta_zip, name='descargar_carpeta_zip'),
    path('drive/acciones-masivas/', views.acciones_masivas_drive, name='acciones_masivas_drive'),
    path('drive/preview/<int:documento_id>/', views.preview_archivo, name='preview_archivo'),
    path('archivo/mover/<int:archivo_id>/', views.mover_archivo_drive, name='mover_archivo_drive'),

    # TAREAS
    path('tarea/crear/<uuid:cliente_id>/', views.gestionar_tarea, name='gestionar_tarea'),
    path('tarea/toggle/<int:tarea_id>/', views.toggle_tarea, name='toggle_tarea'),
    path('tarea/editar/<int:tarea_id>/', views.editar_tarea, name='editar_tarea'),
    path('tarea/eliminar/<int:tarea_id>/', views.eliminar_tarea, name='eliminar_tarea'),
    path('cliente/<uuid:cliente_id>/generar-link/', views.generar_link_externo, name='generar_link_externo'),
    path('portal-cliente/<uuid:token>/', views.vista_publica_carga, name='vista_publica_carga'),
    path('aprobar-archivo/<int:temp_id>/', views.aprobar_archivo_temporal, name='aprobar_archivo_temporal'),
    
    # MÓDULOS
    path('contratos/generar/<uuid:cliente_id>/', views.generador_contratos, name='generador_contratos'),
    path('contratos/visor/<int:documento_id>/', views.visor_docx, name='visor_docx'),
    path('plantillas/subir/', views.subir_plantilla, name='subir_plantilla'),
    path('plantillas/eliminar/<int:plantilla_id>/', views.eliminar_plantilla, name='eliminar_plantilla'),
    path('rechazar-archivo/<int:temp_id>/', views.rechazar_archivo_temporal, name='rechazar_archivo_temporal'),
    path('drive/preview/<int:archivo_id>/', views.obtener_preview_archivo, name='obtener_preview_archivo'),
    
    # HERRAMIENTAS Y API
    path('herramientas/disenador/', views.diseñador_plantillas, name='diseñador_plantillas'),
    path('api/previsualizar-word/', views.previsualizar_word_raw, name='previsualizar_word_raw'),
    path('api/crear-variable/', views.crear_variable_api, name='api_crear_variable'),
    path('api/convertir-html/', views.api_convertir_html, name='api_convertir_html'), 
    path('archivo/descargar/<int:archivo_id>/', views.descargar_archivo_oficial, name='descargar_archivo_oficial'),
    path('api/buscar-cliente/', views.buscar_cliente_api, name='buscar_cliente_api'),
    path('herramientas/qr/', views.generador_qr, name='generador_qr'),
    
    # COTIZACIONES
    path('carpeta/<int:carpeta_id>/redactar-correo/', views.redactar_correo_autorizaciones, name='redactar_correo_autorizaciones'),
    path('cotizaciones/servicios/', views.gestion_servicios, name='gestion_servicios'),
    path('cotizaciones/servicios/guardar/', views.guardar_servicio, name='guardar_servicio'),
    path('cotizaciones/servicios/eliminar/<int:servicio_id>/', views.eliminar_servicio, name='eliminar_servicio'),
    path('cotizaciones/', views.lista_cotizaciones, name='lista_cotizaciones'),
    path('cotizaciones/nueva/', views.nueva_cotizacion, name='nueva_cotizacion'),
    path('cotizaciones/<int:cotizacion_id>/', views.detalle_cotizacion, name='detalle_cotizacion'),
    path('cotizaciones/<int:cotizacion_id>/pdf/', views.generar_pdf_cotizacion, name='pdf_cotizacion'),
    path('cotizaciones/<int:cotizacion_id>/convertir/', views.convertir_a_cliente, name='convertir_cliente'),
    path('cotizaciones/<int:cotizacion_id>/enviar-email/', views.enviar_cotizacion_email, name='enviar_cotizacion_email'),
    path('cotizaciones/eliminar/<int:cotizacion_id>/', views.eliminar_cotizacion, name='eliminar_cotizacion'),

    # FINANZAS
    path('finanzas/', views.panel_finanzas, name='panel_finanzas'),
    path('finanzas/pagar/', views.registrar_pago, name='registrar_pago'),
    path('finanzas/recibo/<int:pago_id>/', views.recibo_pago_pdf, name='recibo_pago_pdf'),
    path('finanzas/cobro/<int:cuenta_id>/<str:tipo_pago>/', views.generar_orden_cobro, name='generar_orden_cobro'),
    path('finanzas/gastos/', views.modulo_gastos, name='modulo_gastos'),
    path('finanzas/gastos/exportar/', views.exportar_gastos_excel, name='exportar_gastos_excel'),
    
    # CORREOS Y ENTREGAS
    path('correo/<uuid:cliente_id>/<str:tipo_correo>/', views.enviar_correo_universal, name='enviar_correo_universal'),
    path('generar-final/', views.generar_contrato_final, name='generar_contrato_final'),
    path('cliente/<uuid:cliente_id>/carpeta/<int:carpeta_id>/preparar-entrega/', views.preparar_entrega_autorizaciones, name='preparar_entrega'),
    path('cliente/<uuid:cliente_id>/enviar-recordatorio/', views.enviar_recordatorio_documentacion, name='enviar_recordatorio'),
    path('cliente/<int:cliente_id>/eliminar-especiales/', views.eliminar_carpetas_especiales, name='eliminar_carpetas_especiales'),
    # AGENDA
    path('agenda/', views.agenda_legal, name='agenda_legal'),
    path('agenda/api/', views.api_eventos, name='api_eventos'),
    path('agenda/crear/', views.crear_evento, name='crear_evento'),
    path('agenda/eliminar/<int:evento_id>/', views.eliminar_evento, name='eliminar_evento'),
    path('agenda/mover/', views.mover_evento_api, name='mover_evento_api'),
    path('cliente/<uuid:cliente_id>/carpetas-especiales/', views.crear_carpetas_especiales, name='crear_carpetas_especiales'),
    # PARCHE DE EMERGENCIA: Acepta la ruta vieja por si el navegador tiene caché
    path('expedientes/drive/subir-requisito/<int:carpeta_id>/', views.subir_archivo_requisito),
]

# ESTO REEMPLAZA TU ANTIGUO RE_PATH PARCHE PARA MEDIA:
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)