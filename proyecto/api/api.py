# API que expone el modelo entrenado
import joblib
import pandas as pd
from fastapi import FastAPI
from pydantic import BaseModel

CLASES = ["setosa", "versicolor", "virginica"]
modelo = joblib.load("modelo.joblib")

app = FastAPI(title="API del modelo Iris")


class Flor(BaseModel):
    largo_sepalo: float
    ancho_sepalo: float
    largo_petalo: float
    ancho_petalo: float


@app.get("/")
def estado():
    return {"estado": "ok"}


@app.post("/predecir")
def predecir(flor: Flor):
    fila = pd.DataFrame([[flor.largo_sepalo, flor.ancho_sepalo,
                          flor.largo_petalo, flor.ancho_petalo]],
                        columns=modelo.feature_names_in_)
    clase = int(modelo.predict(fila)[0])
    return {"especie": CLASES[clase]}
