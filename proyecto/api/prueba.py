# Cliente que envía una solicitud POST con JSON a la API
import requests

URL = "http://127.0.0.1:8001/predecir"

# Datos de entrada: un diccionario de Python que requests convierte en JSON
flor = {
    "largo_sepalo": 6.7,
    "ancho_sepalo": 3.0,
    "largo_petalo": 5.2,
    "ancho_petalo": 2.3,
}

respuesta = requests.post(URL, json=flor, timeout=10)

print("Código de estado:", respuesta.status_code)
print("Respuesta:", respuesta.json())