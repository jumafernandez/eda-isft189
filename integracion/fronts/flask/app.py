# Front con Flask: el servidor arma las páginas y es el único que habla con
# la API. El navegador nunca ve la clave: solo recibe HTML ya resuelto.
import base64
import csv
import io
import json
import time

import anthropic
from flask import Flask, render_template, request

import conversacion
from cliente_api import API_URL, ErrorDeApi, llamar_api

MAXIMO_POR_LOTE = 500  # el mismo tope que fija la API

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 2 * 1024 * 1024  # archivos de hasta 2 MB


def valores_iniciales(info):
    """La mediana de cada variable: un punto de partida razonable."""
    valores = {}
    for variable in info["variables"]:
        valores[variable["nombre"]] = variable["mediana"]
    return valores


def agrupar(variables):
    """Separa las variables en los grupos del formulario, sin perder el orden."""
    grupos = {}
    for variable in variables:
        grupos.setdefault(variable["grupo"], []).append(variable)
    return grupos


# --- Un vino ---

@app.route("/")
def inicio():
    try:
        info = llamar_api("GET", "/v1/model-info")
    except ErrorDeApi as error:
        return render_template("sin_api.html", error=error), 503
    return render_template("inicio.html", info=info,
                           grupos=agrupar(info["variables"]),
                           valores=valores_iniciales(info))


@app.route("/ejemplo/<int:numero>")
def ejemplo(numero):
    """Devuelve solo los campos del formulario, con los valores de un ejemplo."""
    info = llamar_api("GET", "/v1/model-info")
    return render_template("_campos.html", grupos=agrupar(info["variables"]),
                           valores=info["ejemplos"][numero]["valores"])


@app.route("/predecir", methods=["POST"])
def predecir():
    """Recibe el formulario y devuelve solo el recuadro del resultado."""
    # Los valores viajan como texto; la API se encarga de validarlos
    vino = request.form.to_dict()
    try:
        prediccion = llamar_api("POST", "/v1/predict", vino)
    except ErrorDeApi as error:
        return render_template("_error.html", error=error)
    return render_template("_resultado.html", prediccion=prediccion)


# --- Lote de vinos desde un CSV ---

def leer_vinos(archivo, columnas):
    """Convierte el CSV subido en una lista de vinos (diccionarios)."""
    texto = archivo.read().decode("utf-8-sig")
    lineas = texto.splitlines()
    if not lineas:
        raise ErrorDeApi("El archivo está vacío.")

    # Excel configurado en castellano separa con punto y coma
    # y escribe los decimales con coma
    separador = ","
    if ";" in lineas[0]:
        separador = ";"

    filas = csv.DictReader(io.StringIO(texto), delimiter=separador)
    faltantes = [nombre for nombre in columnas
                 if nombre not in (filas.fieldnames or [])]
    if faltantes:
        raise ErrorDeApi("Al archivo le faltan columnas: "
                         + ", ".join(faltantes) + ".")

    vinos = []
    for fila in filas:
        vino = {}
        for nombre in columnas:
            valor = (fila[nombre] or "").strip()
            if separador == ";":
                valor = valor.replace(",", ".")
            vino[nombre] = valor
        vinos.append(vino)
    if not vinos:
        raise ErrorDeApi("El archivo no tiene filas de datos.")
    return vinos


def predecir_por_tandas(vinos):
    """Envía los vinos a la API en tandas, respetando su tope por pedido."""
    predicciones = []
    for desde in range(0, len(vinos), MAXIMO_POR_LOTE):
        tanda = vinos[desde:desde + MAXIMO_POR_LOTE]
        try:
            respuesta = llamar_api("POST", "/v1/predict/batch", {"vinos": tanda})
        except ErrorDeApi as error:
            raise ErrorDeApi(error.mensaje, ubicar_en_archivo(error.detalle, desde))
        predicciones.extend(respuesta["predicciones"])
    return predicciones


def ubicar_en_archivo(detalle, desde):
    """Traduce "vinos[3].ph" al número de fila que la persona ve en su planilla."""
    traducido = []
    for problema in detalle:
        campo = problema["campo"]
        if campo.startswith("vinos["):
            posicion, _, variable = campo[6:].partition("].")
            # +1 por el encabezado y +1 porque las planillas cuentan desde 1
            fila = desde + int(posicion) + 2
            campo = f"fila {fila}, {variable}"
        traducido.append({"campo": campo, "mensaje": problema["mensaje"]})
    return traducido


def armar_csv(vinos, predicciones, columnas, clases):
    """Arma el CSV de salida: las columnas originales más la predicción."""
    salida = io.StringIO()
    escritor = csv.writer(salida)
    encabezado = columnas + ["calidad"]
    for clase in clases:
        encabezado.append(f"probabilidad_{clase}")
    escritor.writerow(encabezado)
    for vino, prediccion in zip(vinos, predicciones):
        fila = [vino[nombre] for nombre in columnas]
        fila.append(prediccion["calidad"])
        for clase in clases:
            fila.append(prediccion["probabilidades"][clase])
        escritor.writerow(fila)
    return salida.getvalue()


@app.route("/lote")
def lote():
    return render_template("lote.html")


@app.route("/lote", methods=["POST"])
def predecir_lote():
    """Recibe el CSV y devuelve el resumen, una vista previa y la descarga."""
    archivo = request.files.get("archivo")
    try:
        if archivo is None or archivo.filename == "":
            raise ErrorDeApi("Elija un archivo CSV antes de enviar.")
        info = llamar_api("GET", "/v1/model-info")
        columnas = [variable["nombre"] for variable in info["variables"]]
        vinos = leer_vinos(archivo, columnas)
        predicciones = predecir_por_tandas(vinos)
    except UnicodeDecodeError:
        error = ErrorDeApi("No se pudo leer el archivo. Guárdelo como CSV UTF-8.")
        return render_template("_error.html", error=error)
    except ErrorDeApi as error:
        return render_template("_error.html", error=error)

    conteo = {}
    for clase in info["clases"]:
        conteo[clase] = 0
    for prediccion in predicciones:
        conteo[prediccion["calidad"]] += 1

    # El CSV viaja dentro del propio enlace de descarga (una "data URI"),
    # así el servidor no necesita guardar archivos entre un pedido y otro
    contenido = armar_csv(vinos, predicciones, columnas, info["clases"])
    descarga = base64.b64encode(contenido.encode("utf-8")).decode("ascii")

    return render_template(
        "_lote_resultado.html", total=len(vinos), conteo=conteo,
        columnas=columnas, descarga=descarga,
        vista_previa=list(zip(vinos, predicciones))[:8],
    )


@app.route("/lote/ejemplo.csv")
def csv_de_ejemplo():
    """Un CSV chico con los vinos de ejemplo, para probar la carga por lote."""
    info = llamar_api("GET", "/v1/model-info")
    columnas = [variable["nombre"] for variable in info["variables"]]
    salida = io.StringIO()
    escritor = csv.writer(salida)
    escritor.writerow(columnas)
    for ejemplo in info["ejemplos"]:
        escritor.writerow([ejemplo["valores"][nombre] for nombre in columnas])
    return salida.getvalue(), {
        "Content-Type": "text/csv; charset=utf-8",
        "Content-Disposition": "attachment; filename=vinos_de_ejemplo.csv",
    }


# --- Conversación con un modelo de lenguaje ---

MAXIMO_DE_MENSAJES = 20   # mensajes previos que se reenvían en cada pedido
MAXIMO_DE_LETRAS = 1000   # largo máximo de cada mensaje


def leer_historial(texto):
    """Reconstruye la conversación previa que el navegador guarda en la página.

    Llega desde el navegador, así que no se confía en ella: solo se aceptan
    mensajes de texto con los dos roles válidos, y en cantidad acotada.
    """
    try:
        mensajes = json.loads(texto or "[]")
    except ValueError:
        return []
    historial = []
    if not isinstance(mensajes, list):
        return historial
    for mensaje in mensajes[-MAXIMO_DE_MENSAJES:]:
        if not isinstance(mensaje, dict):
            continue
        rol = mensaje.get("role")
        contenido = mensaje.get("content")
        if rol not in ("user", "assistant"):
            continue
        if isinstance(contenido, str) and contenido:
            historial.append({"role": rol, "content": contenido[:4000]})
    return historial


@app.route("/conversar")
def conversar():
    return render_template("conversar.html", hay_clave=conversacion.HAY_CLAVE)


@app.route("/conversar", methods=["POST"])
def enviar_mensaje():
    """Recibe un mensaje y devuelve el intercambio nuevo, como trozo de HTML."""
    mensaje = request.form.get("mensaje", "").strip()[:MAXIMO_DE_LETRAS]
    historial = leer_historial(request.form.get("historial"))
    if not mensaje:
        return ""

    usadas = []
    falla = None
    respuesta = ""
    try:
        respuesta, usadas = conversacion.responder(historial, mensaje)
    except ErrorDeApi as error:
        falla = error.mensaje
    except anthropic.APIError as error:
        falla = conversacion.explicar_falla(error)

    # La conversación solo crece si hubo respuesta
    if not falla:
        historial = historial + [
            {"role": "user", "content": mensaje},
            {"role": "assistant", "content": respuesta},
        ]
    return render_template(
        "_intercambio.html", mensaje=mensaje, respuesta=respuesta,
        usadas=usadas, falla=falla,
        historial=json.dumps(historial, ensure_ascii=False),
    )


# --- Estado del servicio y ficha del modelo ---

@app.route("/modelo")
def modelo():
    inicio = time.perf_counter()
    try:
        llamar_api("GET", "/v1/health")
        demora = round((time.perf_counter() - inicio) * 1000)
        info = llamar_api("GET", "/v1/model-info")
    except ErrorDeApi as error:
        return render_template("sin_api.html", error=error), 503
    return render_template("modelo.html", info=info, demora=demora,
                           api_url=API_URL)


@app.errorhandler(ErrorDeApi)
def api_caida(error):
    """Si la API falla en una ruta que no lo previó, se muestra el aviso."""
    return render_template("_error.html", error=error)
