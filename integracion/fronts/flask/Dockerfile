FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY *.py ./
COPY templates/ templates/
COPY static/ static/

# Usuario sin privilegios
RUN useradd --create-home usuario
USER usuario

EXPOSE 8001

# --workers y --threads: dos procesos con cuatro hilos cada uno. Los navegadores
# abren conexiones por anticipado, sin enviar nada todavía; con un solo proceso
# sin hilos, una de esas conexiones deja esperando a todos los demás pedidos.
CMD ["sh", "-c", "gunicorn --bind 0.0.0.0:${PORT:-8001} --workers 2 --threads 4 --timeout 120 app:app"]
