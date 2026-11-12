# Errores de la API: todos salen con la misma forma y en castellano
#   {"error": "codigo", "mensaje": "explicación", "detalle": [...]}
import logging

from fastapi import Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException

registro = logging.getLogger("api-vinos")

# Nombre corto de cada código HTTP que usa la API
CODIGOS = {
    401: "no_autorizado",
    403: "prohibido",
    404: "no_encontrado",
    405: "metodo_no_permitido",
    429: "demasiados_pedidos",
}

# Traducción de los errores de validación más comunes de Pydantic
MENSAJES = {
    "missing": "Falta este dato.",
    "float_parsing": "Debe ser un número.",
    "float_type": "Debe ser un número.",
    "greater_than_equal": "Debe ser mayor o igual a {ge}.",
    "less_than_equal": "Debe ser menor o igual a {le}.",
    "too_short": "Debe tener al menos {min_length} elemento.",
    "too_long": "Admite como máximo {max_length} elementos.",
    "list_type": "Debe ser una lista.",
    "model_attributes_type": "Debe ser un objeto con los datos de un vino.",
    "json_invalid": "El cuerpo del pedido no es un JSON válido.",
}


def nombre_del_campo(ubicacion):
    """Convierte ("body", "vinos", 3, "alcohol") en "vinos[3].alcohol"."""
    nombre = ""
    for parte in ubicacion:
        if parte == "body":
            continue
        if isinstance(parte, int):
            nombre += f"[{parte}]"
        elif nombre:
            nombre += f".{parte}"
        else:
            nombre = str(parte)
    return nombre or "cuerpo"


def limites(problema):
    """Límites del error, con los enteros sin decimales: 20 y no 20.0."""
    valores = {}
    for clave, valor in problema.get("ctx", {}).items():
        if isinstance(valor, float) and valor.is_integer():
            valor = int(valor)
        valores[clave] = valor
    return valores


def error_http(request: Request, error: HTTPException):
    """Errores que la propia API decide devolver: 401, 403, 404, 429."""
    contenido = {
        "error": CODIGOS.get(error.status_code, "error"),
        "mensaje": str(error.detail),
        "detalle": [],
    }
    if error.status_code == 404 and error.detail == "Not Found":
        contenido["mensaje"] = "La ruta no existe. Consulte /docs."
    return JSONResponse(contenido, status_code=error.status_code,
                        headers=error.headers)


def error_de_validacion(request: Request, error: RequestValidationError):
    """Datos que no cumplen el contrato: 422 con el detalle campo por campo."""
    detalle = []
    for problema in error.errors():
        plantilla = MENSAJES.get(problema["type"], problema["msg"])
        campo = nombre_del_campo(problema["loc"])
        if problema["type"] == "json_invalid":
            campo = "cuerpo"
        detalle.append({
            "campo": campo,
            "mensaje": plantilla.format(**limites(problema)),
        })
    contenido = {
        "error": "datos_invalidos",
        "mensaje": f"Hay {len(detalle)} dato(s) para corregir.",
        "detalle": detalle,
    }
    return JSONResponse(contenido, status_code=422)


def error_inesperado(request: Request, error: Exception):
    """Cualquier otra falla: se registra completa y se responde sin detalles."""
    registro.exception("Error inesperado en %s", request.url.path)
    contenido = {
        "error": "error_interno",
        "mensaje": "Ocurrió un error inesperado. Intente de nuevo más tarde.",
        "detalle": [],
    }
    return JSONResponse(contenido, status_code=500)


def registrar(app):
    """Conecta cada tipo de error con la función que lo responde."""
    app.add_exception_handler(HTTPException, error_http)
    app.add_exception_handler(RequestValidationError, error_de_validacion)
    app.add_exception_handler(Exception, error_inesperado)
