# Configuración común de las pruebas.
# Las pruebas no importan el código de la API: le hablan por HTTP, igual que
# cualquier cliente. Por eso sirven tanto para la API local como para la
# desplegada: alcanza con cambiar BASE_URL.
import os

import httpx
import pytest
from dotenv import load_dotenv

load_dotenv()  # lee integracion/.env si existe

BASE_URL = os.getenv("BASE_URL", "http://localhost:8000")
API_KEY = os.getenv("API_KEY", "")
API_KEY_PUBLICA = os.getenv("API_KEY_PUBLICA", "")
ORIGENES = os.getenv("ORIGENES_PERMITIDOS", "http://localhost:8080")
ORIGEN_PERMITIDO = ORIGENES.split(",")[0].strip()

VINO = {
    "acidez_fija": 7.0,
    "acidez_volatil": 0.29,
    "acido_citrico": 0.31,
    "ph": 3.21,
    "dioxido_azufre_libre": 29,
    "dioxido_azufre_total": 118,
    "sulfatos": 0.51,
    "cloruros": 0.047,
    "azucar_residual": 3.0,
    "densidad": 0.9949,
    "alcohol": 10.3,
}


@pytest.fixture(scope="session")
def cliente():
    """Cliente HTTP que envía la clave privada en todos los pedidos."""
    with httpx.Client(base_url=BASE_URL, timeout=60,
                      headers={"X-API-Key": API_KEY}) as cliente:
        yield cliente


@pytest.fixture(scope="session")
def cliente_sin_clave():
    with httpx.Client(base_url=BASE_URL, timeout=60) as cliente:
        yield cliente


@pytest.fixture
def vino():
    """Un vino válido. Se entrega una copia para que cada prueba la modifique."""
    return dict(VINO)
