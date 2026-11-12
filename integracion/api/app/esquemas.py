# Contrato de la API: la forma de los datos que entran y de los que salen
from typing import Literal

from pydantic import BaseModel, Field

MAXIMO_POR_LOTE = 500

VINO_DE_EJEMPLO = {
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


# --- Entrada ---

class Vino(BaseModel):
    """Las once mediciones fisicoquímicas de un vino."""

    acidez_fija: float = Field(ge=0, le=20, description="Acidez fija (g/L)")
    acidez_volatil: float = Field(ge=0, le=2, description="Acidez volátil (g/L)")
    acido_citrico: float = Field(ge=0, le=2, description="Ácido cítrico (g/L)")
    ph: float = Field(ge=2, le=5, description="pH")
    dioxido_azufre_libre: float = Field(
        ge=0, le=300, description="Dióxido de azufre libre (mg/L)")
    dioxido_azufre_total: float = Field(
        ge=0, le=500, description="Dióxido de azufre total (mg/L)")
    sulfatos: float = Field(ge=0, le=3, description="Sulfatos (g/L)")
    cloruros: float = Field(ge=0, le=1, description="Cloruros (g/L)")
    azucar_residual: float = Field(
        ge=0, le=70, description="Azúcar residual (g/L)")
    densidad: float = Field(ge=0.98, le=1.05, description="Densidad (g/mL)")
    alcohol: float = Field(
        ge=0, le=20, description="Graduación alcohólica (% vol.)")

    # Ejemplo que muestra la documentación en /docs
    model_config = {"json_schema_extra": {"examples": [VINO_DE_EJEMPLO]}}


class Lote(BaseModel):
    """Varios vinos en un solo pedido."""

    vinos: list[Vino] = Field(min_length=1, max_length=MAXIMO_POR_LOTE)


# --- Salida ---

class Probabilidades(BaseModel):
    baja: float
    media: float
    alta: float


class Prediccion(BaseModel):
    calidad: Literal["baja", "media", "alta"]
    probabilidades: Probabilidades


class RespuestaPrediccion(Prediccion):
    version_modelo: str


class RespuestaLote(BaseModel):
    cantidad: int
    version_modelo: str
    predicciones: list[Prediccion]


class Estado(BaseModel):
    estado: str
    version_modelo: str


class Variable(BaseModel):
    nombre: str
    etiqueta: str
    unidad: str
    grupo: str
    minimo: float
    maximo: float
    mediana: float


class Ejemplo(BaseModel):
    nombre: str
    valores: Vino


class InfoModelo(BaseModel):
    nombre: str
    version: str
    fecha_entrenamiento: str
    dataset: str
    scikit_learn: str
    clases: list[str]
    variables: list[Variable]
    filas_entrenamiento: int
    filas_prueba: int
    accuracy_prueba: float
    f1_macro_prueba: float
    matriz_confusion: list[list[int]]
    ejemplos: list[Ejemplo]


# --- Errores: todos los errores de la API tienen esta misma forma ---

class DetalleError(BaseModel):
    campo: str
    mensaje: str


class Error(BaseModel):
    error: str
    mensaje: str
    detalle: list[DetalleError] = []
