# Configuración de la API: todo lo que cambia entre entornos se lee de
# variables de entorno, nunca se escribe en el código
import os

from dotenv import load_dotenv

# En su computadora, lee el archivo integracion/.env si existe.
# En la nube no hay archivo: las variables se cargan en el panel de la plataforma.
load_dotenv()


def leer_lista(nombre):
    """Convierte el texto "a, b, c" de una variable de entorno en una lista."""
    elementos = []
    for parte in os.getenv(nombre, "").split(","):
        parte = parte.strip()
        if parte:
            elementos.append(parte)
    return elementos


# Clave privada: la usan los servidores (Flask, Next.js). Permite todo.
API_KEY = os.getenv("API_KEY", "")

# Clave pública: la usa el widget, que corre en el navegador y por eso
# cualquiera puede verla. Tiene límite de pedidos y no puede predecir por lote.
API_KEY_PUBLICA = os.getenv("API_KEY_PUBLICA", "")

# Sitios web autorizados a consultar la API desde el navegador (CORS)
ORIGENES_PERMITIDOS = leer_lista("ORIGENES_PERMITIDOS")

# Pedidos por minuto que puede hacer cada dirección IP con la clave pública
LIMITE_POR_MINUTO = int(os.getenv("LIMITE_POR_MINUTO", "30"))

if not API_KEY:
    raise RuntimeError(
        "Falta la variable de entorno API_KEY. "
        "Copie .env.example como .env y complete los valores."
    )
