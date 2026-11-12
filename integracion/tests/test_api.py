# Pruebas del contrato de la API: qué responde ante cada tipo de pedido
import pytest

from conftest import API_KEY_PUBLICA, ORIGEN_PERMITIDO

CLASES = ["baja", "media", "alta"]


# --- Estado y metadatos ---

def test_health_responde_sin_clave(cliente_sin_clave):
    respuesta = cliente_sin_clave.get("/v1/health")
    assert respuesta.status_code == 200
    assert respuesta.json()["estado"] == "ok"


def test_model_info_describe_el_modelo(cliente):
    respuesta = cliente.get("/v1/model-info")
    assert respuesta.status_code == 200

    info = respuesta.json()
    assert info["clases"] == CLASES
    assert len(info["variables"]) == 11
    assert 0 <= info["accuracy_prueba"] <= 1
    assert 0 <= info["f1_macro_prueba"] <= 1
    # Matriz de confusión de 3 x 3: una fila y una columna por clase
    assert len(info["matriz_confusion"]) == 3
    for fila in info["matriz_confusion"]:
        assert len(fila) == 3


# --- Predicción de un vino ---

def test_prediccion_valida(cliente, vino):
    respuesta = cliente.post("/v1/predict", json=vino)
    assert respuesta.status_code == 200

    resultado = respuesta.json()
    assert resultado["calidad"] in CLASES
    assert sum(resultado["probabilidades"].values()) == pytest.approx(1, abs=0.01)


def test_los_ejemplos_del_modelo_dan_la_clase_esperada(cliente):
    """Comprueba que el modelo desplegado es el mismo que se entrenó."""
    info = cliente.get("/v1/model-info").json()
    for ejemplo in info["ejemplos"]:
        respuesta = cliente.post("/v1/predict", json=ejemplo["valores"])
        # El nombre del ejemplo termina con su clase: "Vino de calidad alta"
        assert ejemplo["nombre"].endswith(respuesta.json()["calidad"])


# --- Datos inválidos: 422 ---

def test_valor_fuera_de_rango_devuelve_422(cliente, vino):
    vino["alcohol"] = 45
    respuesta = cliente.post("/v1/predict", json=vino)
    assert respuesta.status_code == 422

    error = respuesta.json()
    assert error["error"] == "datos_invalidos"
    assert error["detalle"][0]["campo"] == "alcohol"


def test_dato_faltante_devuelve_422(cliente, vino):
    del vino["ph"]
    respuesta = cliente.post("/v1/predict", json=vino)
    assert respuesta.status_code == 422
    assert respuesta.json()["detalle"][0]["campo"] == "ph"


def test_texto_en_lugar_de_numero_devuelve_422(cliente, vino):
    vino["densidad"] = "mucha"
    respuesta = cliente.post("/v1/predict", json=vino)
    assert respuesta.status_code == 422


# --- Predicción por lote ---

def test_lote_devuelve_una_prediccion_por_vino(cliente, vino):
    respuesta = cliente.post("/v1/predict/batch", json={"vinos": [vino] * 3})
    assert respuesta.status_code == 200

    resultado = respuesta.json()
    assert resultado["cantidad"] == 3
    assert len(resultado["predicciones"]) == 3


def test_lote_vacio_devuelve_422(cliente):
    respuesta = cliente.post("/v1/predict/batch", json={"vinos": []})
    assert respuesta.status_code == 422


def test_lote_demasiado_grande_devuelve_422(cliente, vino):
    respuesta = cliente.post("/v1/predict/batch", json={"vinos": [vino] * 501})
    assert respuesta.status_code == 422


def test_lote_indica_que_vino_tiene_el_error(cliente, vino):
    vino_malo = dict(vino)
    vino_malo["ph"] = 9
    respuesta = cliente.post("/v1/predict/batch",
                             json={"vinos": [vino, vino_malo]})
    assert respuesta.status_code == 422
    assert respuesta.json()["detalle"][0]["campo"] == "vinos[1].ph"


# --- Claves: 401 y 403 ---

def test_sin_clave_devuelve_401(cliente_sin_clave, vino):
    respuesta = cliente_sin_clave.post("/v1/predict", json=vino)
    assert respuesta.status_code == 401
    assert respuesta.json()["error"] == "no_autorizado"


def test_clave_incorrecta_devuelve_401(cliente_sin_clave, vino):
    respuesta = cliente_sin_clave.post(
        "/v1/predict", json=vino, headers={"X-API-Key": "clave-inventada"})
    assert respuesta.status_code == 401


@pytest.mark.skipif(not API_KEY_PUBLICA, reason="No hay clave pública configurada")
def test_clave_publica_no_puede_predecir_por_lote(cliente_sin_clave, vino):
    respuesta = cliente_sin_clave.post(
        "/v1/predict/batch", json={"vinos": [vino]},
        headers={"X-API-Key": API_KEY_PUBLICA})
    assert respuesta.status_code == 403


# --- CORS ---
# Antes de un POST con JSON, el navegador envía un pedido OPTIONS de consulta
# (preflight) para preguntar si ese sitio tiene permiso. Estas pruebas lo imitan.

def consulta_previa(cliente, origen):
    return cliente.options("/v1/predict", headers={
        "Origin": origen,
        "Access-Control-Request-Method": "POST",
        "Access-Control-Request-Headers": "content-type,x-api-key",
    })


def test_cors_autoriza_un_origen_de_la_lista(cliente_sin_clave):
    respuesta = consulta_previa(cliente_sin_clave, ORIGEN_PERMITIDO)
    assert respuesta.status_code == 200
    assert respuesta.headers["access-control-allow-origin"] == ORIGEN_PERMITIDO


def test_cors_rechaza_un_origen_que_no_esta_en_la_lista(cliente_sin_clave):
    respuesta = consulta_previa(cliente_sin_clave, "https://sitio-ajeno.example")
    assert "access-control-allow-origin" not in respuesta.headers
