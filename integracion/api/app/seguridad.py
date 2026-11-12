# Seguridad de la API: claves de acceso y límite de pedidos
import secrets
import time

from fastapi import Depends, Header, HTTPException, Request

from app import config

# Momento (en segundos) de los últimos pedidos de cada dirección IP.
# Vive en la memoria del proceso: se vacía si la API se reinicia.
pedidos_por_ip = {}


def son_iguales(clave_recibida, clave_esperada):
    """Compara dos claves sin revelar, por la demora, cuánto coinciden."""
    return secrets.compare_digest(clave_recibida.encode(), clave_esperada.encode())


def tipo_de_clave(clave):
    """Devuelve "privada", "publica" o None si la clave no es válida."""
    if not clave:
        return None
    if son_iguales(clave, config.API_KEY):
        return "privada"
    if config.API_KEY_PUBLICA and son_iguales(clave, config.API_KEY_PUBLICA):
        return "publica"
    return None


def limitar_pedidos(request):
    """Corta con 429 si esta dirección IP superó el límite por minuto."""
    ip = request.client.host
    ahora = time.time()

    recientes = []
    for momento in pedidos_por_ip.get(ip, []):
        if ahora - momento < 60:
            recientes.append(momento)

    if len(recientes) >= config.LIMITE_POR_MINUTO:
        raise HTTPException(
            status_code=429,
            detail="Demasiados pedidos. Espere un minuto y vuelva a intentar.",
            headers={"Retry-After": "60"},
        )

    recientes.append(ahora)
    pedidos_por_ip[ip] = recientes


def exigir_clave(request: Request, x_api_key: str | None = Header(default=None)):
    """Corta con 401 si falta el encabezado X-API-Key o la clave es incorrecta."""
    tipo = tipo_de_clave(x_api_key)
    if tipo is None:
        raise HTTPException(
            status_code=401,
            detail="Falta la clave o es incorrecta. "
                   "Envíela en el encabezado X-API-Key.",
        )
    if tipo == "publica":
        limitar_pedidos(request)
    return tipo


def exigir_clave_privada(tipo: str = Depends(exigir_clave)):
    """Corta con 403 si la clave es válida pero no es la privada."""
    if tipo != "privada":
        raise HTTPException(
            status_code=403,
            detail="Esta operación necesita la clave privada.",
        )
    return tipo
