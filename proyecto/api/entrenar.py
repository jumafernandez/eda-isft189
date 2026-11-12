# Entrena el modelo y lo guarda en modelo.joblib, con sus metadatos
import json

import joblib
import sklearn
from sklearn.datasets import load_iris
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split

X, y = load_iris(return_X_y=True, as_frame=True)
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

modelo = RandomForestClassifier(n_estimators=100, random_state=42)
modelo.fit(X_train, y_train)
accuracy = modelo.score(X_test, y_test)
print(f"Accuracy en prueba: {accuracy:.3f}")

joblib.dump(modelo, "modelo.joblib")

# Metadatos en un JSON legible: es lo que la API devuelve en /modelo
info = {
    "nombre": "Clasificador de flores Iris",
    "version": "1.0",
    "variables": list(X.columns),
    "clases": ["setosa", "versicolor", "virginica"],
    "accuracy_prueba": round(accuracy, 3),
    "scikit_learn": sklearn.__version__,
}
with open("modelo_info.json", "w", encoding="utf-8") as f:
    json.dump(info, f, ensure_ascii=False, indent=2)
