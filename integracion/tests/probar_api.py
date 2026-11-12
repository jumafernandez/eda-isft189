# Revisión rápida de una API ya levantada, local o desplegada.
#
#   python tests/probar_api.py                              (API local)
#   python tests/probar_api.py https://mi-api.onrender.com  (API desplegada)
#
# La clave se toma de la variable de entorno API_KEY o del archivo .env.
import os
import sys
import time

import httpx
from dotenv import load_dotenv

load_dotenv()

BASE_URL = "http://localhost:8000"
if len(sys.argv) > 1:
    BASE_URL = sys.argv[1].rstrip("/")
API_KEY = os.getenv("API_KEY", "")

VINO = {
    "acidez_fija": 7.0, "acidez_volatil": 0.29, "acido_citrico": 0.31,
    "ph": 3.21, "dioxido_azufre_libre": 29, "dioxido_azufre_total": 118,
    "sulfatos": 0.51, "cloruros": 0.047, "azucar_residual": 3.0,
    "densidad": 0.9949, "alcohol": 10.3,
}

resultados = []


def revisar(descripcion, cumple, dato=""):
    """Anota y muestra el resultado de una revisión."""
    resultados.append(cumple)
    marca = "OK   " if cumple else "FALLA"
    print(f"  [{marca}] {descripcion} {dato}")


print(f"Revisando {BASE_URL}\n")

with httpx.Client(base_url=BASE_URL, timeout=90) as cliente:
    con_clave = {"X-API-Key": API_KEY}

    # 1. ¿Está activa? El primer pedido a un servicio gratuito puede tardar
    #    cerca de un minuto, porque la plataforma lo apaga cuando no se usa.
    inicio = time.perf_counter()
    try:
        respuesta = cliente.get("/v1/health")
    except httpx.HTTPError as error:
        print(f"  [FALLA] No se pudo conectar: {error}")
        sys.exit(1)
    demora = time.perf_counter() - inicio
    revisar("La API responde en /v1/health", respuesta.status_code == 200,
            f"({demora:.1f} s)")

    # 2. Metadatos
    respuesta = cliente.get("/v1/model-info", headers=con_clave)
    revisar("Devuelve los metadatos del modelo", respuesta.status_code == 200)
    if respuesta.status_code == 200:
        info = respuesta.json()
        print(f"          {info['nombre']}, versión {info['version']}, "
              f"accuracy {info['accuracy_prueba']}")

    # 3. Predicción válida
    respuesta = cliente.post("/v1/predict", json=VINO, headers=con_clave)
    revisar("Predice un vino válido", respuesta.status_code == 200)
    if respuesta.status_code == 200:
        print(f"          calidad: {respuesta.json()['calidad']}")

    # 4. Datos inválidos
    vino_malo = dict(VINO)
    vino_malo["alcohol"] = 45
    respuesta = cliente.post("/v1/predict", json=vino_malo, headers=con_clave)
    revisar("Rechaza un valor fuera de rango con 422",
            respuesta.status_code == 422)

    # 5. Lote
    respuesta = cliente.post("/v1/predict/batch", json={"vinos": [VINO] * 5},
                             headers=con_clave)
    revisar("Predice un lote de 5 vinos", respuesta.status_code == 200)

    # 6. Sin clave
    respuesta = cliente.post("/v1/predict", json=VINO)
    revisar("Rechaza un pedido sin clave con 401", respuesta.status_code == 401)

    # 7. CORS: un sitio que no está en la lista no recibe autorización
    respuesta = cliente.options("/v1/predict", headers={
        "Origin": "https://sitio-ajeno.example",
        "Access-Control-Request-Method": "POST",
    })
    revisar("No autoriza por CORS a un sitio ajeno",
            "access-control-allow-origin" not in respuesta.headers)

    # 8. Latencia de 20 predicciones
    demoras = []
    for _ in range(20):
        inicio = time.perf_counter()
        cliente.post("/v1/predict", json=VINO, headers=con_clave)
        demoras.append((time.perf_counter() - inicio) * 1000)
    demoras.sort()
    promedio = sum(demoras) / len(demoras)
    revisar("Responde en menos de un segundo en promedio", promedio < 1000,
            f"(promedio {promedio:.0f} ms, la más lenta {demoras[-1]:.0f} ms)")

correctas = sum(resultados)
print(f"\n{correctas} de {len(resultados)} revisiones correctas")
if correctas < len(resultados):
    sys.exit(1)
