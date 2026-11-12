# Escenario conversacional: una persona le pregunta al modelo con sus palabras.
#
# Intervienen dos modelos distintos:
#   - el modelo de lenguaje (Claude), que entiende la pregunta y redacta la
#     respuesta;
#   - el modelo de calidad de vinos, que es el único que estima calidades.
#
# El modelo de lenguaje no inventa predicciones. Cuando necesita una, pide que
# se ejecute una "herramienta": una función de este archivo, que consulta la
# API del modelo de vinos. Con el resultado en mano, redacta la respuesta.
import json
import os

import anthropic
from anthropic import beta_tool

from cliente_api import ErrorDeApi, llamar_api

MODELO_DE_LENGUAJE = "claude-opus-5-5"
PUNTOS = 8  # tramos que recorre la herramienta de exploración

# La clave se lee de la variable de entorno ANTHROPIC_API_KEY.
# Sin clave, la aplicación funciona igual y esta pantalla avisa que falta.
HAY_CLAVE = bool(os.getenv("ANTHROPIC_API_KEY"))

INSTRUCCIONES = """\
Usted es el asistente del laboratorio de la bodega Los Aromos. Conversa con \
personas del laboratorio y de enología que quieren aprovechar un modelo \
estadístico que estima la calidad de un vino (baja, media o alta) a partir de \
once mediciones fisicoquímicas.

Las estimaciones de calidad salen únicamente de ese modelo, al que usted \
accede con las herramientas. No estime calidades por su cuenta: el valor de \
este asistente es que cada número proviene del modelo y se puede rastrear.

Ficha del modelo:
{ficha}

Al responder:
- Responda en castellano, de usted, en pocas oraciones y sin formato Markdown, \
porque la respuesta se muestra como texto simple.
- Si faltan mediciones, la herramienta las completa con el valor mediano. \
Dígale a la persona cuáles se supusieron, porque cambian la estimación.
- Presente cada resultado como la estimación de un modelo estadístico, con su \
probabilidad, y no como un veredicto.
- La exploración de una medición muestra cómo responde el modelo, no una \
relación de causa y efecto: en un vino real las mediciones cambian juntas.
- Si le preguntan algo ajeno a los vinos o al modelo, dígalo con amabilidad y \
vuelva al tema.
"""


def armar_instrucciones(info):
    """Completa las instrucciones con los datos que publica la API del modelo."""
    lineas = [
        f"{info['nombre']}, versión {info['version']}, entrenado el "
        f"{info['fecha_entrenamiento']} con {info['filas_entrenamiento']} vinos.",
        f"En {info['filas_prueba']} vinos de prueba: accuracy "
        f"{info['accuracy_prueba']}, F1 macro {info['f1_macro_prueba']}.",
        f"Matriz de confusión (filas: calidad real; columnas: predicha; orden "
        f"{info['clases']}): {info['matriz_confusion']}.",
        "Mediciones (nombre para las herramientas, descripción, rango y mediana):",
    ]
    for variable in info["variables"]:
        lineas.append(
            f"- {variable['nombre']}: {variable['etiqueta']} {variable['unidad']}, "
            f"de {variable['minimo']} a {variable['maximo']}, "
            f"mediana {variable['mediana']}")
    return INSTRUCCIONES.format(ficha="\n".join(lineas))


def completar(mediciones, info):
    """Arma el vino completo: lo que falta se reemplaza por la mediana."""
    vino = {}
    supuestas = []
    for variable in info["variables"]:
        nombre = variable["nombre"]
        if nombre in mediciones:
            vino[nombre] = mediciones[nombre]
        else:
            vino[nombre] = variable["mediana"]
            supuestas.append(nombre)
    return vino, supuestas


def como_texto(resultado):
    """Las herramientas le devuelven su resultado al modelo de lenguaje en JSON."""
    return json.dumps(resultado, ensure_ascii=False)


# --- Herramientas: lo único que el modelo de lenguaje puede hacer con el
# --- modelo de vinos. El texto de cada función es lo que lee para decidir
# --- cuándo usarla y con qué datos.

@beta_tool
def predecir_calidad(mediciones: dict[str, float]) -> str:
    """Estima la calidad de un vino (baja, media o alta) con el modelo de la bodega.

    Args:
        mediciones: Mediciones conocidas del vino, por nombre de variable, por
            ejemplo {"alcohol": 12.5, "ph": 3.2}. Las que falten se completan
            con la mediana y se informan en "mediciones_supuestas".
    """
    try:
        info = llamar_api("GET", "/v1/model-info")
        vino, supuestas = completar(mediciones, info)
        prediccion = llamar_api("POST", "/v1/predict", vino)
    except ErrorDeApi as error:
        return como_texto({"error": error.mensaje, "detalle": error.detalle})
    prediccion["mediciones_supuestas"] = supuestas
    return como_texto(prediccion)


@beta_tool
def explorar_medicion(variable: str, mediciones: dict[str, float]) -> str:
    """Muestra cómo cambia la calidad estimada al mover una sola medición.

    Recorre el rango de esa medición, del mínimo al máximo, dejando fijas
    las demás, y devuelve la calidad y las probabilidades en cada punto.

    Args:
        variable: Nombre de la medición que se mueve, por ejemplo "alcohol".
        mediciones: Mediciones conocidas del vino, por nombre de variable. Las
            que falten se completan con la mediana.
    """
    try:
        info = llamar_api("GET", "/v1/model-info")
        rango = None
        for candidata in info["variables"]:
            if candidata["nombre"] == variable:
                rango = candidata
        if rango is None:
            return como_texto({"error": f"No existe la medición {variable}."})

        vino, supuestas = completar(mediciones, info)
        valores = []
        variantes = []
        for paso in range(PUNTOS + 1):
            avance = paso / PUNTOS
            valor = rango["minimo"] + (rango["maximo"] - rango["minimo"]) * avance
            valores.append(round(valor, 4))
            variantes.append({**vino, variable: valor})
        lote = llamar_api("POST", "/v1/predict/batch", {"vinos": variantes})
    except ErrorDeApi as error:
        return como_texto({"error": error.mensaje, "detalle": error.detalle})

    curva = []
    for valor, prediccion in zip(valores, lote["predicciones"]):
        curva.append({"valor": valor, "calidad": prediccion["calidad"],
                      "probabilidades": prediccion["probabilidades"]})
    return como_texto({"variable": variable, "unidad": rango["unidad"],
                       "curva": curva, "mediciones_supuestas": supuestas})


HERRAMIENTAS = [predecir_calidad, explorar_medicion]


def responder(historial, mensaje):
    """Devuelve la respuesta del asistente y la lista de herramientas que usó.

    El historial es la conversación previa: una lista de mensajes con "role"
    ("user" o "assistant") y "content" (el texto).
    """
    info = llamar_api("GET", "/v1/model-info")
    cliente = anthropic.Anthropic()  # toma la clave de ANTHROPIC_API_KEY

    # El "tool runner" del SDK maneja el ida y vuelta: envía la conversación,
    # y cada vez que el modelo de lenguaje pide una herramienta, la ejecuta,
    # le devuelve el resultado y vuelve a consultar, hasta que hay respuesta.
    conversacion = cliente.beta.messages.tool_runner(
        model=MODELO_DE_LENGUAJE,
        max_tokens=16000,
        system=armar_instrucciones(info),
        tools=HERRAMIENTAS,
        messages=historial + [{"role": "user", "content": mensaje}],
        output_config={"effort": "low"},  # preguntas simples: respuesta ágil
        max_iterations=6,
        # Si el modelo declina un pedido por razones de seguridad, la API lo
        # reintenta con otro modelo dentro de la misma llamada
        betas=["server-side-fallback-2026-07-01"],
        fallbacks="default",
    )

    usadas = []
    ultima = None
    for respuesta in conversacion:
        ultima = respuesta
        for bloque in respuesta.content:
            if bloque.type == "tool_use":
                usadas.append({"nombre": bloque.name, "datos": bloque.input})

    if ultima is None or ultima.stop_reason == "refusal":
        return "No puedo ayudar con ese pedido.", usadas
    partes = [bloque.text for bloque in ultima.content if bloque.type == "text"]
    return "".join(partes).strip(), usadas


def explicar_falla(error):
    """Convierte un error del servicio de lenguaje en un mensaje para la persona."""
    if isinstance(error, anthropic.AuthenticationError):
        return "La clave del modelo de lenguaje no es válida."
    if isinstance(error, anthropic.RateLimitError):
        return "El modelo de lenguaje recibió demasiados pedidos. Espere."
    if isinstance(error, anthropic.APIConnectionError):
        return "No se pudo conectar con el modelo de lenguaje."
    if isinstance(error, anthropic.APIStatusError):
        return f"El modelo de lenguaje devolvió un error ({error.status_code})."
    return "No se pudo completar la respuesta."
