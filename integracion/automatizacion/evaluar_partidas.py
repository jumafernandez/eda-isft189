# Escenario "de sistema a sistema": un programa usa el modelo sin que nadie
# abra una pantalla. Simula la tarea diaria del laboratorio de la bodega:
# toma cada planilla de la carpeta entrada/, le pide las predicciones a la API
# y deja en salida/ la misma planilla con la calidad estimada de cada vino.
#
#   python automatizacion/evaluar_partidas.py
#
# Está pensado para que lo ejecute otro programa a una hora fija (el
# Programador de tareas de Windows, cron en Linux o un flujo de n8n). Por eso
# no pregunta nada, informa por pantalla y, si algo falla, termina con un
# código de error que ese otro programa puede detectar.
import csv
import os
import sys
from pathlib import Path

import requests
from dotenv import load_dotenv

load_dotenv()  # lee integracion/.env si existe

API_URL = os.getenv("API_URL", "http://localhost:8000")
API_KEY = os.getenv("API_KEY", "")
MAXIMO_POR_LOTE = 500  # el tope que fija la API

CARPETA = Path(__file__).parent  # carpeta donde está este archivo
ENTRADA = CARPETA / "entrada"
SALIDA = CARPETA / "salida"


def pedir(metodo, ruta, datos=None):
    """Hace un pedido a la API con la clave privada y devuelve el JSON."""
    respuesta = requests.request(
        metodo, API_URL + ruta, json=datos,
        headers={"X-API-Key": API_KEY}, timeout=60,
    )
    if respuesta.status_code != 200:
        raise RuntimeError(
            f"la API respondió {respuesta.status_code}: {respuesta.text}")
    return respuesta.json()


def evaluar(planilla, columnas, clases):
    """Evalúa los vinos de una planilla y escribe el resultado en salida/."""
    with open(planilla, encoding="utf-8-sig", newline="") as archivo:
        filas = list(csv.DictReader(archivo))

    # Se envían de a tandas, para respetar el tope de vinos por pedido
    predicciones = []
    for desde in range(0, len(filas), MAXIMO_POR_LOTE):
        vinos = []
        for fila in filas[desde:desde + MAXIMO_POR_LOTE]:
            vinos.append({nombre: fila[nombre] for nombre in columnas})
        respuesta = pedir("POST", "/v1/predict/batch", {"vinos": vinos})
        predicciones.extend(respuesta["predicciones"])

    # La planilla de salida conserva todas las columnas y agrega la calidad
    conteo = {clase: 0 for clase in clases}
    with open(SALIDA / planilla.name, "w", encoding="utf-8", newline="") as archivo:
        escritor = csv.writer(archivo)
        escritor.writerow(list(filas[0]) + ["calidad"])
        for fila, prediccion in zip(filas, predicciones):
            escritor.writerow(list(fila.values()) + [prediccion["calidad"]])
            conteo[prediccion["calidad"]] += 1
    return conteo


planillas = sorted(ENTRADA.glob("*.csv"))
if not planillas:
    print("No hay planillas para evaluar en", ENTRADA)
    sys.exit(0)

SALIDA.mkdir(exist_ok=True)
try:
    # Los nombres de las columnas y de las clases se le preguntan al modelo
    info = pedir("GET", "/v1/model-info")
    columnas = [variable["nombre"] for variable in info["variables"]]
    print(f"Modelo {info['nombre']}, versión {info['version']}")

    for planilla in planillas:
        conteo = evaluar(planilla, columnas, info["clases"])
        partes = [f"{cantidad} {clase}" for clase, cantidad in conteo.items()]
        total = sum(conteo.values())
        print(f"  {planilla.name}: {total} vinos ({', '.join(partes)})")
except (requests.RequestException, RuntimeError, KeyError) as error:
    print(f"No se pudo completar la evaluación: {error}", file=sys.stderr)
    sys.exit(1)

print("Resultados en", SALIDA)
