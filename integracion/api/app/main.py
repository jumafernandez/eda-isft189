# API del modelo de calidad de vinos: el servicio y sus rutas
import logging
import time

from fastapi import APIRouter, Depends, FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from app import config, errores, esquemas, modelo, seguridad

logging.basicConfig(level=logging.INFO,
                    format="%(asctime)s %(levelname)s %(message)s")
registro = logging.getLogger("api-vinos")

VERSION_MODELO = modelo.metadatos["version"]

app = FastAPI(
    title="API de calidad de vinos",
    version="1.0.0",
    description="Clasifica un vino como de calidad baja, media o alta "
                "a partir de once mediciones fisicoquímicas.",
)
errores.registrar(app)

# CORS: solo los sitios de la lista pueden consultar la API desde el navegador
app.add_middleware(
    CORSMiddleware,
    allow_origins=config.ORIGENES_PERMITIDOS,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type", "X-API-Key"],
)


@app.middleware("http")
async def registrar_pedido(request: Request, siguiente):
    """Anota cada pedido: método, ruta, código de respuesta y demora."""
    inicio = time.perf_counter()
    respuesta = await siguiente(request)
    demora = (time.perf_counter() - inicio) * 1000
    registro.info("%s %s -> %s (%.1f ms)", request.method, request.url.path,
                  respuesta.status_code, demora)
    return respuesta


# Respuestas de error que se documentan en /docs para todas las rutas con clave
ERRORES_CON_CLAVE = {
    401: {"model": esquemas.Error, "description": "Falta la clave o es incorrecta"},
    429: {"model": esquemas.Error, "description": "Demasiados pedidos"},
}
ERROR_DE_DATOS = {
    422: {"model": esquemas.Error, "description": "Datos inválidos"},
}

# Todas las rutas empiezan con /v1. Si algún día cambia el contrato,
# la versión nueva se publica en /v2 y los clientes actuales siguen funcionando.
v1 = APIRouter(prefix="/v1")


@v1.get("/health", response_model=esquemas.Estado, tags=["Estado"])
def estado():
    """Indica si el servicio está activo. No pide clave."""
    return {"estado": "ok", "version_modelo": VERSION_MODELO}


@v1.get("/model-info", response_model=esquemas.InfoModelo, tags=["Modelo"],
        responses=ERRORES_CON_CLAVE,
        dependencies=[Depends(seguridad.exigir_clave)])
def informacion_del_modelo():
    """Devuelve los metadatos del modelo: variables, clases y métricas."""
    return modelo.metadatos


@v1.post("/predict", response_model=esquemas.RespuestaPrediccion,
         tags=["Predicción"], responses={**ERRORES_CON_CLAVE, **ERROR_DE_DATOS},
         dependencies=[Depends(seguridad.exigir_clave)])
def predecir(vino: esquemas.Vino):
    """Predice la calidad de un vino."""
    prediccion = modelo.predecir([vino.model_dump()])[0]
    prediccion["version_modelo"] = VERSION_MODELO
    return prediccion


@v1.post("/predict/batch", response_model=esquemas.RespuestaLote,
         tags=["Predicción"],
         responses={**ERRORES_CON_CLAVE, **ERROR_DE_DATOS,
                    403: {"model": esquemas.Error,
                          "description": "Necesita la clave privada"}},
         dependencies=[Depends(seguridad.exigir_clave_privada)])
def predecir_lote(lote: esquemas.Lote):
    """Predice la calidad de varios vinos en un solo pedido."""
    vinos = [vino.model_dump() for vino in lote.vinos]
    predicciones = modelo.predecir(vinos)
    return {
        "cantidad": len(predicciones),
        "version_modelo": VERSION_MODELO,
        "predicciones": predicciones,
    }


app.include_router(v1)


@app.get("/", include_in_schema=False)
def inicio():
    return {
        "servicio": "API de calidad de vinos",
        "documentacion": "/docs",
        "estado": "/v1/health",
    }
