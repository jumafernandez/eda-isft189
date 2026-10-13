# Entrena el modelo y lo guarda en modelo.joblib
import joblib
from sklearn.datasets import load_iris
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split

X, y = load_iris(return_X_y=True, as_frame=True)
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

modelo = RandomForestClassifier(n_estimators=100, random_state=42)
modelo.fit(X_train, y_train)
print(f"Accuracy en prueba: {modelo.score(X_test, y_test):.3f}")

joblib.dump(modelo, "modelo.joblib")
