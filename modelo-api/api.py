# API que sirve el modelo entrenado
import json

import joblib
import pandas as pd
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

# El modelo se carga una sola vez, al iniciar la API
modelo = joblib.load("modelo.joblib")
with open("modelo_info.json", encoding="utf-8") as f:
    info = json.load(f)

app = FastAPI(title="API de calidad de vinos")

# Permite que una página web abierta en el navegador consulte la API
app.add_middleware(CORSMiddleware, allow_origins=["*"],
                   allow_methods=["*"], allow_headers=["*"])


# Datos que espera la API: nombre, tipo y rango de cada variable
class Vino(BaseModel):
    alcohol: float = Field(ge=0, le=20, description="Graduación alcohólica (%)")
    volatile_acidity: float = Field(ge=0, le=2, description="Acidez volátil (g/L)")
    sulphates: float = Field(ge=0, le=3, description="Sulfatos (g/L)")
    citric_acid: float = Field(ge=0, le=2, description="Ácido cítrico (g/L)")


@app.get("/")
def estado():
    return {"estado": "ok"}


@app.get("/modelo")
def datos_del_modelo():
    return info


@app.post("/predecir")
def predecir(vino: Vino):
    fila = pd.DataFrame([vino.model_dump()])[info["variables"]]
    clase = modelo.predict(fila)[0]
    probabilidades = modelo.predict_proba(fila)[0]
    return {
        "calidad": clase,
        "probabilidades": {c: round(float(p), 3)
                           for c, p in zip(modelo.classes_, probabilidades)},
    }
