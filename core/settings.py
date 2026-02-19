import os
from pathlib import Path
import environ
import dj_database_url
from django.core.exceptions import ImproperlyConfigured

# ==========================================
# 1. CONFIGURACIÓN DEL ENTORNO
# ==========================================
BASE_DIR = Path(__file__).resolve().parent.parent

env = environ.Env()
# Lee el archivo .env si existe (para desarrollo local)
environ.Env.read_env(os.path.join(BASE_DIR, '.env'))

# --- CORRECCIÓN DE SEGURIDAD 1: DEBUG ---
# Por defecto FALSE. Solo será True si el .env lo dice explícitamente.
# IMPORTANTE: En tu PC, tu archivo .env debe tener: DEBUG=True
DEBUG = env.bool('DEBUG', default=False)

# --- CORRECCIÓN DE SEGURIDAD 2: SECRET_KEY ---
# En producción (DEBUG=False), fallará si no hay clave. En local usa la insegura.
if DEBUG:
    SECRET_KEY = env('SECRET_KEY', default='django-insecure-clave-desarrollo-temporal')
else:
    try:
        SECRET_KEY = env('SECRET_KEY')
    except ImproperlyConfigured:
        raise ImproperlyConfigured("Falta la variable SECRET_KEY en entorno de producción.")

# --- CORRECCIÓN DE SEGURIDAD 3: ALLOWED_HOSTS ---
# Evita el '*' en producción. Lee una lista separada por comas del entorno.
# Ejemplo en .env: ALLOWED_HOSTS=mi-app.railway.app,midominio.com
ALLOWED_HOSTS = env.list('ALLOWED_HOSTS', default=['localhost', '127.0.0.1', '.railway.app'])


# Si usas Railway, es bueno agregar esto para evitar errores de CSRF en formularios
# Nota: Ajusta esto a tus dominios reales cuando tengas la URL final
CSRF_TRUSTED_ORIGINS = ['https://*.railway.app', 'https://*.up.railway.app']


# ==========================================
# 2. APLICACIONES INSTALADAS
# ==========================================
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.humanize',
    'django_apscheduler',
    # --- CLOUDINARY (Importante: cloudinary_storage antes de staticfiles) ---
    'cloudinary_storage',
    'django.contrib.staticfiles',
    'cloudinary',
    # -----------------------------------------------------------------------

    # Librerías de Terceros
    'whitenoise.runserver_nostatic', 
    'anymail',  # Para Resend
    
    # Mis Aplicaciones
    'expedientes',
]


# ==========================================
# 3. MIDDLEWARE (Intermediarios)
# ==========================================
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    "whitenoise.middleware.WhiteNoiseMiddleware", 
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    # NOTA: Si X_FRAME_OPTIONS = 'SAMEORIGIN' aún falla, puedes comentar la siguiente línea
    # para desactivar la protección de clickjacking completamente (bajo tu riesgo):
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'core.urls'


# ==========================================
# 4. TEMPLATES (Plantillas HTML)
# ==========================================
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                # Tu procesador de notificaciones
                'expedientes.context_processors.notificaciones_globales',
            ],
        },
    },
]

WSGI_APPLICATION = 'core.wsgi.application'


# ==========================================
# 5. BASE DE DATOS (Configuración Híbrida)
# ==========================================
# Por defecto usa SQLite (Local)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Si existe DATABASE_URL (Railway/Nube), sobrescribe la configuración para usar PostgreSQL
if 'DATABASE_URL' in os.environ:
    db_from_env = dj_database_url.config(conn_max_age=600, ssl_require=True)
    DATABASES['default'].update(db_from_env)


# ==========================================
# 6. AUTENTICACIÓN Y PASSWORD
# ==========================================
AUTH_USER_MODEL = 'expedientes.Usuario'

AUTH_PASSWORD_VALIDATORS = [
    { 'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator', },
    { 'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator', },
    { 'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator', },
    { 'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator', },
]

# Redirecciones
LOGIN_URL = 'login'
LOGIN_REDIRECT_URL = 'dashboard'
LOGOUT_REDIRECT_URL = 'login'


# ==========================================
# 7. INTERNACIONALIZACIÓN
# ==========================================
LANGUAGE_CODE = 'es-mx'
TIME_ZONE = 'America/Mexico_City'
USE_I18N = True
USE_TZ = True


# ==========================================
# 8. ARCHIVOS ESTÁTICOS Y MEDIA (Whitenoise + Cloudinary)
# ==========================================
STATIC_URL = 'static/'

# Dónde buscar estáticos en desarrollo
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static')]

# Dónde recolectar estáticos para producción (Railway usará esto)
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# Motor de almacenamiento para producción (Comprime y optimiza)
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# --- CONFIGURACIÓN DE MEDIA (CLOUDINARY) ---
CLOUDINARY_STORAGE = {
    'CLOUD_NAME': env('CLOUDINARY_CLOUD_NAME', default=''),
    'API_KEY':    env('CLOUDINARY_API_KEY', default=''),
    'API_SECRET': env('CLOUDINARY_API_SECRET', default=''),
    'SECURE': True,  # <--- CRÍTICO: Fuerza HTTPS en las URLs de imágenes/PDFs
    'MEDIA_TAG': 'media',
}

# Si hay credenciales, usamos Cloudinary. Si no, seguimos en local.
if CLOUDINARY_STORAGE['CLOUD_NAME']:
    DEFAULT_FILE_STORAGE = 'cloudinary_storage.storage.MediaCloudinaryStorage'
    MEDIA_URL = '/media/'  # Cloudinary manejará la URL real automáticamente
else:
    # Configuración Local Clásica
    MEDIA_URL = '/media/'
    MEDIA_ROOT = os.path.join(BASE_DIR, 'media')


# ==========================================
# 9. SISTEMA DE CORREO (Vía API - RESEND)
# ==========================================
EMAIL_BACKEND = "anymail.backends.resend.EmailBackend"

ANYMAIL = {
   "RESEND_API_KEY": env('RESEND_API_KEY', default=''),
}

# CONFIGURACIÓN DEL REMITENTE
DEFAULT_FROM_EMAIL = env('DEFAULT_FROM_EMAIL', default="GESTIONES CORPAD <onboarding@resend.dev>")
SERVER_EMAIL = env('DEFAULT_FROM_EMAIL', default="onboarding@resend.dev")

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


# ==========================================
# 10. CONFIGURACIÓN GLOBAL DE IFRAMES (VISOR PDF)
# ==========================================
# Esto soluciona el error "refused to connect" en el visor.
# Aplica tanto para local como producción.
X_FRAME_OPTIONS = 'SAMEORIGIN'
XS_SHARING_ALLOWED_METHODS = ['POST','GET','OPTIONS', 'PUT', 'DELETE']


# ==========================================
# 11. SEGURIDAD PARA PRODUCCIÓN (BLINDAJE)
# ==========================================
# Este bloque se activa SOLO si DEBUG=False (en Railway/Producción)

if not DEBUG:
    # 1. Forzar HTTPS siempre
    SECURE_SSL_REDIRECT = True
    # Confiar en el proxy de Railway
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
    
    # 2. HSTS (Seguridad Estricta de Transporte)
    SECURE_HSTS_SECONDS = 31536000
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True

    # 3. Cookies Seguras (Encriptadas)
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    
    # 4. Cabeceras extra contra ataques
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True

# --- FIN DEL ARCHIVO ---
# ==========================================
# 12. CORRECCIÓN PARA WINDOWS (LOCAL)
# ==========================================
import mimetypes
mimetypes.add_type("application/pdf", ".pdf", True)
mimetypes.add_type("application/vnd.openxmlformats-officedocument.wordprocessingml.document", ".docx", True)
mimetypes.add_type("image/svg+xml", ".svg", True)
mimetypes.add_type("text/javascript", ".js", True) # Ayuda si tus JS no cargan