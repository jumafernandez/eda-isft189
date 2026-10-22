# Entrena el modelo de calidad de vinos y lo guarda en disco
import json
from datetime import datetime

import joblib
import sklearn
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from ucimlrepo import fetch_ucirepo

# 1. Datos: Wine Quality (UCI), el mismo dataset de la notebook modelo
wine = fetch_ucirepo(id=186)
df = wine.data.features.copy()
df["quality"] = wine.data.targets["quality"]

# Variable objetivo categórica, igual que en la notebook
df["calidad"] = df["quality"].apply(
    lambda x: "baja" if x <= 4 else "media" if x <= 6 else "alta"
)

# Para que el ejemplo sea simple usamos solo cuatro variables
VARIABLES = ["alcohol", "volatile_acidity", "sulphates", "citric_acid"]
X = df[VARIABLES]
y = df["calidad"]

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

# 2. Pipeline: la transformación y el modelo viajan juntos
modelo = Pipeline([
    ("escalado", StandardScaler()),
    ("clasificador", LogisticRegression(max_iter=1000, class_weight="balanced")),
])
modelo.fit(X_train, y_train)

accuracy = accuracy_score(y_test, modelo.predict(X_test))
print(f"Accuracy en prueba: {accuracy:.3f}")

# 3. Persistencia: el modelo en un archivo binario...
joblib.dump(modelo, "modelo.joblib")

# ...y sus metadatos en un JSON legible
info = {
    "nombre": "Clasificador de calidad de vinos",
    "version": "1.0",
    "fecha_entrenamiento": datetime.now().isoformat(timespec="seconds"),
    "variables": VARIABLES,
    "clases": list(modelo.classes_),
    "accuracy_prueba": round(accuracy, 3),
    "scikit_learn": sklearn.__version__,
}
with open("modelo_info.json", "w", encoding="utf-8") as f:
    json.dump(info, f, ensure_ascii=False, indent=2)

print("Modelo guardado en modelo.joblib y metadatos en modelo_info.json")
