# Prueba de latencia: cuánto tarda la API en responder una predicción
import os
import statistics
import time

PEDIDOS = 30
PROMEDIO_MAXIMO_MS = float(os.getenv("LATENCIA_PROMEDIO_MS", "500"))
P95_MAXIMO_MS = float(os.getenv("LATENCIA_P95_MS", "1000"))


def test_latencia_promedio_y_p95(cliente, vino):
    # El primer pedido no se mide: puede incluir el arranque del servicio
    cliente.post("/v1/predict", json=vino)

    demoras = []
    for _ in range(PEDIDOS):
        inicio = time.perf_counter()
        respuesta = cliente.post("/v1/predict", json=vino)
        demoras.append((time.perf_counter() - inicio) * 1000)
        assert respuesta.status_code == 200

    promedio = statistics.mean(demoras)
    # p95: el 95 % de los pedidos tardó eso o menos. Muestra los casos lentos
    # que el promedio esconde.
    p95 = statistics.quantiles(demoras, n=20)[-1]
    print(f"\nLatencia de {PEDIDOS} pedidos: promedio {promedio:.0f} ms, "
          f"p95 {p95:.0f} ms")

    assert promedio < PROMEDIO_MAXIMO_MS
    assert p95 < P95_MAXIMO_MS
