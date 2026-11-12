# Descarga el dataset Wine Quality (UCI) y lo guarda como CSV en castellano.
# Se ejecuta una sola vez: el archivo resultante ya está en el repositorio,
# para que entrenar el modelo no dependa de tener conexión con UCI.
from pathlib import Path

from ucimlrepo import fetch_ucirepo

CARPETA = Path(__file__).parent  # carpeta donde está este archivo

# Nombre original de cada variable y su nombre en castellano
NOMBRES = {
    "fixed_acidity": "acidez_fija",
    "volatile_acidity": "acidez_volatil",
    "citric_acid": "acido_citrico",
    "residual_sugar": "azucar_residual",
    "chlorides": "cloruros",
    "free_sulfur_dioxide": "dioxido_azufre_libre",
    "total_sulfur_dioxide": "dioxido_azufre_total",
    "density": "densidad",
    "pH": "ph",
    "sulphates": "sulfatos",
    "alcohol": "alcohol",
}

vinos = fetch_ucirepo(id=186)
datos = vinos.data.features.rename(columns=NOMBRES)
datos["puntaje"] = vinos.data.targets["quality"]

datos.to_csv(CARPETA / "datos" / "vinos.csv", index=False)
print(f"Guardadas {len(datos)} filas en datos/vinos.csv")
