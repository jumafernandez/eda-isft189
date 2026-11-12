# Lógica del modelo: cargarlo y predecir.
# Este archivo no sabe nada de HTTP: se puede usar y probar sin levantar la API.
import json
from pathlib import Path

import joblib
import pandas as pd

# integracion/modelo, la carpeta donde entrenar.py deja sus dos archivos
CARPETA_MODELO = Path(__file__).resolve().parents[2] / "modelo"

# El modelo y sus metadatos se cargan una sola vez, al iniciar la API
modelo = joblib.load(CARPETA_MODELO / "modelo.joblib")
with open(CARPETA_MODELO / "metadatos.json", encoding="utf-8") as archivo:
    metadatos = json.load(archivo)

# Columnas en el mismo orden usado al entrenar
COLUMNAS = [variable["nombre"] for variable in metadatos["variables"]]


def predecir(vinos):
    """Recibe una lista de vinos (diccionarios) y devuelve sus predicciones."""
    tabla = pd.DataFrame(vinos)[COLUMNAS]
    clases = modelo.predict(tabla)
    probabilidades = modelo.predict_proba(tabla)

    predicciones = []
    for clase, fila in zip(clases, probabilidades):
        por_clase = {}
        for nombre, valor in zip(modelo.classes_, fila):
            por_clase[str(nombre)] = round(float(valor), 3)
        predicciones.append({"calidad": str(clase), "probabilidades": por_clase})
    return predicciones
