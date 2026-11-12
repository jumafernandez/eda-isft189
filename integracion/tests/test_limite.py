# Prueba del límite de pedidos de la clave pública.
# Agota el cupo de un minuto, por eso solo corre si se la pide:
#   PROBAR_LIMITE=1 pytest tests/test_limite.py
import os

import pytest

from conftest import API_KEY_PUBLICA

LIMITE = int(os.getenv("LIMITE_POR_MINUTO", "30"))


@pytest.mark.skipif(os.getenv("PROBAR_LIMITE") != "1",
                    reason="Se activa con PROBAR_LIMITE=1")
def test_clave_publica_tiene_limite_de_pedidos(cliente_sin_clave, vino):
    codigos = []
    for _ in range(LIMITE + 5):
        respuesta = cliente_sin_clave.post(
            "/v1/predict", json=vino, headers={"X-API-Key": API_KEY_PUBLICA})
        codigos.append(respuesta.status_code)

    assert codigos[0] == 200
    assert codigos[-1] == 429
    assert respuesta.json()["error"] == "demasiados_pedidos"
