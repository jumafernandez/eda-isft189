# Cliente de la API del modelo de calidad de vinos.
# Lo usan las pantallas de app.py y las herramientas de conversacion.py.
import os

import requests
from dotenv import load_dotenv

load_dotenv()  # lee integracion/.env si existe

API_URL = os.getenv("API_URL", "http://localhost:8000")
API_KEY = os.getenv("API_KEY", "")


class ErrorDeApi(Exception):
    """La API no respondió o respondió con un error."""

    def __init__(self, mensaje, detalle=None):
        super().__init__(mensaje)
        self.mensaje = mensaje
        self.detalle = detalle or []


def llamar_api(metodo, ruta, datos=None):
    """Hace un pedido a la API con la clave privada y devuelve el JSON."""
    try:
        respuesta = requests.request(
            metodo, API_URL + ruta, json=datos,
            headers={"X-API-Key": API_KEY}, timeout=60,
        )
    except requests.RequestException:
        raise ErrorDeApi("No se pudo conectar con la API del modelo. "
                         "Verifique que esté levantada.")

    try:
        contenido = respuesta.json()
    except ValueError:
        contenido = {}  # la respuesta no era JSON: no es nuestra API
    if respuesta.status_code != 200:
        mensaje = contenido.get(
            "mensaje", f"La API respondió con el código {respuesta.status_code}.")
        raise ErrorDeApi(mensaje, contenido.get("detalle"))
    return contenido
