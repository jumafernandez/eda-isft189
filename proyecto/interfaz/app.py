# Interfaz web que consume la API
import os

import requests
import streamlit as st

API_URL = os.getenv("API_URL", "http://localhost:8000")

st.title("Clasificador de flores Iris")

largo_sepalo = st.number_input("Largo del sépalo (cm)", value=5.1)
ancho_sepalo = st.number_input("Ancho del sépalo (cm)", value=3.5)
largo_petalo = st.number_input("Largo del pétalo (cm)", value=1.4)
ancho_petalo = st.number_input("Ancho del pétalo (cm)", value=0.2)

if st.button("Predecir"):
    datos = {
        "largo_sepalo": largo_sepalo,
        "ancho_sepalo": ancho_sepalo,
        "largo_petalo": largo_petalo,
        "ancho_petalo": ancho_petalo,
    }
    respuesta = requests.post(f"{API_URL}/predecir", json=datos, timeout=10)
    st.success(f"Especie predicha: {respuesta.json()['especie']}")
