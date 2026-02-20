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
environ.Env.read_env(os.path.join(BASE_DIR, '.env'))

DEBUG = env.bool('DEBUG', default=False)

if DEBUG:
    SECRET_KEY = env('SECRET_KEY', default='django-insecure-clave-desarrollo-temporal')
else:
    try:
        SECRET_KEY = env('SECRET_KEY')
    except ImproperlyConfigured:
        raise ImproperlyConfigured("Falta la variable SECRET_KEY en entorno de producción.")

ALLOWED_HOSTS = env.list('ALLOWED_HOSTS', default=['localhost', '127.0.0.1', '.railway.app'])

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

    # WhiteNoise PRIMERO, antes de staticfiles
    'whitenoise.runserver_nostatic',

    # Cloudinary (cloudinary_storage antes de staticfiles)
    'cloudinary_storage',
    'django.contrib.staticfiles',
    'cloudinary',

    # Librerías de Terceros
    'anymail',

    # Mis Aplicaciones
    'expedientes',
]


# ==========================================
# 3. MIDDLEWARE
# ==========================================
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'core.urls'


# ==========================================
# 4. TEMPLATES
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
                'expedientes.context_processors.notificaciones_globales',
            ],
        },
    },
]

WSGI_APPLICATION = 'core.wsgi.application'


# ==========================================
# 5. BASE DE DATOS
# ==========================================
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

if 'DATABASE_URL' in os.environ:
    db_from_env = dj_database_url.config(conn_max_age=600, ssl_require=True)
    DATABASES['default'].update(db_from_env)


# ==========================================
# 6. AUTENTICACIÓN Y PASSWORD
# ==========================================
AUTH_USER_MODEL = 'expedientes.Usuario'

AUTH_PASSWORD_VALIDATORS = [
    { 'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator' },
    { 'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator' },
    { 'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator' },
    { 'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator' },
]

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
# 8. ARCHIVOS ESTÁTICOS Y MEDIA
# ==========================================
STATIC_URL = '/static/'
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static')]
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
WHITENOISE_ROOT = os.path.join(BASE_DIR, 'static')

# --- CLOUDINARY solo para archivos subidos por usuarios (media) ---
CLOUDINARY_STORAGE = {
    'CLOUD_NAME':               env('CLOUDINARY_CLOUD_NAME', default=''),
    'API_KEY':                  env('CLOUDINARY_API_KEY', default=''),
    'API_SECRET':               env('CLOUDINARY_API_SECRET', default=''),
    'SECURE':                   True,
    'MEDIA_TAG':                'media',
    'STATIC_TAG':               '',
    'UPLOAD_PREFIX':            'media',
    'STATICFILES_MANIFEST_ROOT': os.path.join(BASE_DIR, 'staticfiles'),
}

if CLOUDINARY_STORAGE['CLOUD_NAME']:
    DEFAULT_FILE_STORAGE = 'cloudinary_storage.storage.MediaCloudinaryStorage'
    MEDIA_URL = '/media/'
else:
    MEDIA_URL = '/media/'
    MEDIA_ROOT = os.path.join(BASE_DIR, 'media')


# ==========================================
# 9. CORREO (Resend vía Anymail)
# ==========================================
EMAIL_BACKEND = "anymail.backends.resend.EmailBackend"

ANYMAIL = {
    "RESEND_API_KEY": env('RESEND_API_KEY', default=''),
}

DEFAULT_FROM_EMAIL = env('DEFAULT_FROM_EMAIL', default="GESTIONES CORPAD <onboarding@resend.dev>")
SERVER_EMAIL = env('DEFAULT_FROM_EMAIL', default="onboarding@resend.dev")

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


# ==========================================
# 10. IFRAMES (Visor PDF)
# ==========================================
X_FRAME_OPTIONS = 'SAMEORIGIN'
XS_SHARING_ALLOWED_METHODS = ['POST', 'GET', 'OPTIONS', 'PUT', 'DELETE']


# ==========================================
# 11. SEGURIDAD EN PRODUCCIÓN
# ==========================================
if not DEBUG:
    SECURE_SSL_REDIRECT = True
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
    SECURE_HSTS_SECONDS = 31536000
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True


# ==========================================
# 12. MIMETYPES (Windows local)
# ==========================================
import mimetypes
mimetypes.add_type("application/pdf", ".pdf", True)
mimetypes.add_type("application/vnd.openxmlformats-officedocument.wordprocessingml.document", ".docx", True)
mimetypes.add_type("image/svg+xml", ".svg", True)
mimetypes.add_type("text/javascript", ".js", True)


# ==========================================
# 13. STATICFILES_STORAGE - AL FINAL
# Usamos StaticFilesStorage básico para máxima compatibilidad
# WhiteNoise sigue sirviendo los archivos vía middleware
# ==========================================
STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.StaticFilesStorage'