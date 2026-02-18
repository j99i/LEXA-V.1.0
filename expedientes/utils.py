# ==========================================
# EXPEDIENTES/UTILS.PY - FUNCIONES UTILITARIAS
# ==========================================
import logging
from django.http import HttpResponse
from django.template.loader import render_to_string
import weasyprint

logger = logging.getLogger(__name__)


def generar_pdf_response(request, template_name, context, filename, disposition='inline'):
    """
    Genera un HttpResponse con un PDF renderizado desde un template HTML.
    
    Uso:
        return generar_pdf_response(request, 'cotizaciones/pdf_template.html', {'c': cotizacion}, 'Cotizacion_1.pdf')
    
    Args:
        request:       HttpRequest de Django (necesario para build_absolute_uri).
        template_name: Ruta del template HTML a renderizar.
        context:       Diccionario de contexto para el template.
        filename:      Nombre del archivo PDF de salida.
        disposition:   'inline' para ver en navegador, 'attachment' para forzar descarga.
    
    Returns:
        HttpResponse con content_type 'application/pdf'.
    """
    try:
        base_url = request.build_absolute_uri('/')
        
        # Inyectar base_url en el contexto para que los templates puedan usarlo
        context['base_url'] = base_url
        
        html_string = render_to_string(template_name, context)
        
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = f'{disposition}; filename="{filename}"'
        
        weasyprint.HTML(string=html_string, base_url=base_url).write_pdf(response)
        
        return response
    
    except Exception as e:
        logger.error(f"Error generando PDF '{filename}' con template '{template_name}': {e}")
        raise


def generar_pdf_bytes(request, template_name, context):
    """
    Genera el contenido de un PDF como bytes (útil para adjuntar en correos o guardar en BD).
    
    Uso:
        pdf_content = generar_pdf_bytes(request, 'cotizaciones/pdf_template.html', {'c': cotizacion})
        email.attach('archivo.pdf', pdf_content, 'application/pdf')
    
    Args:
        request:       HttpRequest de Django.
        template_name: Ruta del template HTML.
        context:       Diccionario de contexto.
    
    Returns:
        bytes con el contenido del PDF.
    """
    try:
        base_url = request.build_absolute_uri('/')
        context['base_url'] = base_url
        
        html_string = render_to_string(template_name, context)
        pdf_bytes = weasyprint.HTML(string=html_string, base_url=base_url).write_pdf()
        
        return pdf_bytes
    
    except Exception as e:
        logger.error(f"Error generando PDF bytes con template '{template_name}': {e}")
        raise
    # expedientes/utils.py
import xml.etree.ElementTree as ET
from decimal import Decimal
from datetime import datetime

def procesar_xml_factura(archivo):
    """
    Lee un archivo XML en memoria y extrae los datos clave del CFDI 4.0/3.3
    Retorna un diccionario con los datos.
    """
    tree = ET.parse(archivo)
    root = tree.getroot()
    
    # Mapeo de namespaces del SAT (vital para que funcione)
    ns = {
        'cfdi': 'http://www.sat.gob.mx/cfd/4', # Puede variar si es 3.3, pero el ejemplo es 4.0
        'tfd': 'http://www.sat.gob.mx/TimbreFiscalDigital'
    }
    
    # Intentar con namespace 3.3 si falla el 4.0 (fallback)
    if 'http://www.sat.gob.mx/cfd/3' in root.tag:
        ns['cfdi'] = 'http://www.sat.gob.mx/cfd/3'

    # Extraer atributos principales
    try:
        fecha_str = root.get('Fecha')
        # Formato SAT suele ser YYYY-MM-DDTHH:MM:SS
        fecha_emision = datetime.strptime(fecha_str, '%Y-%m-%dT%H:%M:%S')
    except:
        fecha_emision = datetime.now()

    subtotal = Decimal(root.get('SubTotal', '0'))
    total = Decimal(root.get('Total', '0'))
    moneda = root.get('Moneda', 'MXN')

    # Datos Emisor
    emisor = root.find('cfdi:Emisor', ns)
    rfc_emisor = emisor.get('Rfc')
    nombre_emisor = emisor.get('Nombre')

    # Datos Receptor
    receptor = root.find('cfdi:Receptor', ns)
    rfc_receptor = receptor.get('Rfc')
    nombre_receptor = receptor.get('Nombre')

    # Impuestos (Si existen)
    impuestos_node = root.find('cfdi:Impuestos', ns)
    total_impuestos = Decimal('0.00')
    if impuestos_node is not None:
        trasladados = impuestos_node.get('TotalImpuestosTrasladados')
        if trasladados:
            total_impuestos = Decimal(trasladados)

    # UUID (Timbre Fiscal) - Este está en el Complemento
    complemento = root.find('cfdi:Complemento', ns)
    tfd = complemento.find('tfd:TimbreFiscalDigital', ns)
    uuid = tfd.get('UUID')

    return {
        'uuid': uuid,
        'fecha_emision': fecha_emision,
        'rfc_emisor': rfc_emisor,
        'nombre_emisor': nombre_emisor,
        'rfc_receptor': rfc_receptor,
        'nombre_receptor': nombre_receptor,
        'subtotal': subtotal,
        'total_impuestos': total_impuestos,
        'total': total,
        'moneda': moneda
    }