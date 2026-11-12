# Entrena el modelo de calidad de vinos y lo guarda junto con sus metadatos
import json
from datetime import date
from pathlib import Path

import joblib
import pandas as pd
import sklearn
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, confusion_matrix, f1_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

CARPETA = Path(__file__).parent  # carpeta donde está este archivo
VERSION = "1.0.0"
CLASES = ["baja", "media", "alta"]

# Cómo se presenta cada variable: etiqueta, unidad y grupo del formulario
VARIABLES = {
    "acidez_fija": ("Acidez fija", "g/L", "Acidez"),
    "acidez_volatil": ("Acidez volátil", "g/L", "Acidez"),
    "acido_citrico": ("Ácido cítrico", "g/L", "Acidez"),
    "ph": ("pH", "", "Acidez"),
    "dioxido_azufre_libre": ("Dióxido de azufre libre", "mg/L", "Conservación"),
    "dioxido_azufre_total": ("Dióxido de azufre total", "mg/L", "Conservación"),
    "sulfatos": ("Sulfatos", "g/L", "Conservación"),
    "cloruros": ("Cloruros", "g/L", "Conservación"),
    "azucar_residual": ("Azúcar residual", "g/L", "Cuerpo"),
    "densidad": ("Densidad", "g/mL", "Cuerpo"),
    "alcohol": ("Alcohol", "% vol.", "Cuerpo"),
}


def categorizar(puntaje):
    """Convierte el puntaje de los catadores (0 a 10) en la etiqueta de calidad."""
    if puntaje <= 4:
        return "baja"
    elif puntaje <= 6:
        return "media"
    else:
        return "alta"


# 1. Datos: Wine Quality (UCI), guardado en datos/vinos.csv
datos = pd.read_csv(CARPETA / "datos" / "vinos.csv")
columnas = list(VARIABLES)
X = datos[columnas]
y = datos["puntaje"].apply(categorizar)

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

# 2. Pipeline: la transformación y el modelo viajan juntos
#    (un bosque aleatorio no necesita escalado; se incluye para mostrar cómo
#    se guarda una transformación junto al modelo)
modelo = Pipeline([
    ("escalado", StandardScaler()),
    ("clasificador", RandomForestClassifier(
        n_estimators=200, class_weight="balanced", random_state=42)),
])
modelo.fit(X_train, y_train)

# 3. Evaluación sobre los datos de prueba
y_pred = modelo.predict(X_test)
accuracy = accuracy_score(y_test, y_pred)
f1_macro = f1_score(y_test, y_pred, average="macro")
matriz = confusion_matrix(y_test, y_pred, labels=CLASES)
print(f"Accuracy en prueba: {accuracy:.3f} | F1 macro: {f1_macro:.3f}")

# 4. Un vino de ejemplo por clase: entre los casos de prueba que el modelo
#    clasifica bien, el que tiene la confianza típica (la mediana) de su clase
probabilidades = pd.DataFrame(
    modelo.predict_proba(X_test), columns=modelo.classes_, index=X_test.index
)
ejemplos = []
for clase in CLASES:
    aciertos = probabilidades[(y_test == clase) & (y_pred == clase)]
    ordenados = aciertos[clase].sort_values()
    fila = ordenados.index[len(ordenados) // 2]
    ejemplos.append({
        "nombre": f"Calidad {clase}",
        "valores": X_test.loc[fila].to_dict(),
    })

# 5. Metadatos: todo lo que un cliente necesita saber sin abrir el modelo
variables = []
for nombre in columnas:
    etiqueta, unidad, grupo = VARIABLES[nombre]
    variables.append({
        "nombre": nombre,
        "etiqueta": etiqueta,
        "unidad": unidad,
        "grupo": grupo,
        "minimo": float(X[nombre].min()),
        "maximo": float(X[nombre].max()),
        "mediana": float(X[nombre].median()),
    })

metadatos = {
    "nombre": "Clasificador de calidad de vinos",
    "version": VERSION,
    "fecha_entrenamiento": date.today().isoformat(),
    "dataset": "Wine Quality (UCI Machine Learning Repository, id 186)",
    "scikit_learn": sklearn.__version__,
    "clases": CLASES,
    "variables": variables,
    "filas_entrenamiento": len(X_train),
    "filas_prueba": len(X_test),
    "accuracy_prueba": round(accuracy, 3),
    "f1_macro_prueba": round(f1_macro, 3),
    # Filas: clase real. Columnas: clase predicha. Ambas en el orden de "clases"
    "matriz_confusion": matriz.tolist(),
    "ejemplos": ejemplos,
}

# 6. Persistencia: el modelo en un archivo binario y los metadatos en un JSON
joblib.dump(modelo, CARPETA / "modelo.joblib")
with open(CARPETA / "metadatos.json", "w", encoding="utf-8") as archivo:
    json.dump(metadatos, archivo, ensure_ascii=False, indent=2)

print("Modelo guardado en modelo.joblib y metadatos en metadatos.json")
