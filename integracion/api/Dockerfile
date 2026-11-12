# Imagen de la API. Se construye desde la carpeta integracion/, porque
# necesita dos carpetas hermanas: modelo/ y api/
FROM python:3.12-slim

WORKDIR /srv

# 1. Librerías (primero, para aprovechar la caché si el código cambia)
COPY api/requirements.txt api/requirements.txt
RUN pip install --no-cache-dir -r api/requirements.txt

# 2. El modelo se entrena al construir la imagen
COPY modelo/ modelo/
RUN python modelo/entrenar.py

# 3. Código de la API
COPY api/app/ api/app/

# 4. Usuario sin privilegios: si alguien logra entrar al contenedor,
#    no puede modificar el sistema
RUN useradd --create-home usuario
USER usuario

WORKDIR /srv/api
EXPOSE 8000

# Las plataformas en la nube indican el puerto con la variable PORT;
# en su computadora se usa el 8000
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
