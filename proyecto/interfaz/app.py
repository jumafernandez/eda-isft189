# Interfaz web que consume la API
import os

import requests
from flask import Flask, render_template, request

API_URL = os.getenv("API_URL", "http://localhost:8000")

app = Flask(__name__)


@app.route("/", methods=["GET", "POST"])
def formulario():
    # Valores con los que se muestra el formulario la primera vez
    datos = {
        "largo_sepalo": 5.1,
        "ancho_sepalo": 3.5,
        "largo_petalo": 1.4,
        "ancho_petalo": 0.2,
    }
    especie = None

    # Al presionar "Predecir", el navegador envía el formulario con POST
    if request.method == "POST":
        for nombre in datos:
            datos[nombre] = float(request.form[nombre])
        respuesta = requests.post(f"{API_URL}/predecir", json=datos, timeout=10)
        especie = respuesta.json()["especie"]

    return render_template("index.html", datos=datos, especie=especie)
