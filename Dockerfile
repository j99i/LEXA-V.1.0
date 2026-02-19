# 1. Usamos Python 3.12 sobre una base Linux ligera (Debian Slim)
FROM python:3.12-slim

# 2. Evita que Python genere archivos .pyc y buffer de salida
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# 3. INSTALACIÓN DE LIBRERÍAS DE SISTEMA
# Incluye todo lo necesario para WeasyPrint (PDFs) y Django
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    python3-cffi \
    python3-brotli \
    libpango-1.0-0 \
    libpangoft2-1.0-0 \
    libpangocairo-1.0-0 \
    libharfbuzz-subset0 \
    libglib2.0-0 \
    libcairo2 \
    libgdk-pixbuf-2.0-0 \
    libffi-dev \
    shared-mime-info \
    fonts-liberation \
    libmagic1 \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# 4. Crear directorio de trabajo
WORKDIR /app

# 5. Instalar dependencias de Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 6. Copiar el código del proyecto
COPY . .

# 7. Recolectar archivos estáticos
RUN SECRET_KEY=clave-temporal-para-build EMAIL_HOST_USER=dummy EMAIL_HOST_PASSWORD=dummy python manage.py collectstatic --noinput

# 8. COMANDO DE INICIO (Con Puerto 8000 FIJO)
# Usamos el puerto 8000 explícitamente para evitar errores de conexión (502)
CMD ["sh", "-c", "python manage.py migrate && python manage.py createsuperuser --noinput || true && gunicorn core.wsgi:application --bind 0.0.0.0:8000"]