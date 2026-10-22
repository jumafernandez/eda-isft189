# Modelo como servicio con FastAPI

Ejemplo de la *Guía práctica: modelos como servicio con FastAPI* (https://jumafernandez.github.io/eda-isft189/guia-fastapi.html).

```bash
pip install -r requirements.txt
python entrenar.py            # genera modelo.joblib y modelo_info.json
uvicorn api:app --reload      # API en http://localhost:8000 (documentación en /docs)
```

Con la API corriendo, abra `index.html` en el navegador.
