// Widget "Catador virtual": un formulario de calidad de vinos que se agrega
// a cualquier página web con una sola línea:
//
//   <script src="widget.js" data-api="https://mi-api" data-clave="CLAVE"></script>
//
// No usa ningún framework. Todo se dibuja dentro de un Shadow DOM, una zona
// aislada que ofrece el navegador: los estilos del widget no alteran la página
// que lo aloja, y los de la página no alteran al widget.
(function () {
  const guion = document.currentScript;
  const API = (guion.dataset.api || "").replace(/\/$/, "");
  const CLAVE = guion.dataset.clave || "";

  const ESTILOS = `
    :host { all: initial; display: block; }
    * { box-sizing: border-box; }
    .caja {
      font-family: "Inter", system-ui, -apple-system, "Segoe UI", sans-serif;
      color: #2b2024; background: #fffdf8; border: 1px solid #e6dccb;
      border-radius: 16px; padding: 22px; max-width: 420px;
      box-shadow: 0 10px 30px rgba(74, 20, 32, .10);
    }
    .marca {
      font-size: 11px; letter-spacing: .14em; text-transform: uppercase;
      color: #b8893b; font-weight: 600; margin: 0;
    }
    h2 {
      font-family: "Playfair Display", Georgia, "Times New Roman", serif;
      font-size: 24px; font-weight: 600; color: #6b1f2e; margin: 4px 0 6px;
    }
    .bajada { font-size: 13.5px; color: #7a6a63; margin: 0 0 16px; line-height: 1.5; }
    .ejemplos { display: flex; gap: 8px; flex-wrap: wrap; margin-bottom: 14px; }
    .ejemplo {
      font: inherit; font-size: 13px; padding: 6px 12px; cursor: pointer;
      border-radius: 999px; border: 1px solid #d9c9b0; background: #faf5ec;
      color: #4a1420;
    }
    .ejemplo:hover, .ejemplo.activo { background: #6b1f2e; color: #fff; border-color: #6b1f2e; }
    details { border-top: 1px solid #efe6d6; padding: 10px 0 2px; }
    summary { cursor: pointer; font-size: 13.5px; font-weight: 600; color: #4a1420; }
    .grupo {
      font-size: 11px; letter-spacing: .1em; text-transform: uppercase;
      color: #b8893b; margin: 14px 0 6px; font-weight: 600;
    }
    .campos { display: grid; grid-template-columns: 1fr 1fr; gap: 10px 12px; }
    label { font-size: 12.5px; color: #5a4a44; display: block; }
    input {
      font: inherit; font-size: 14px; width: 100%; margin-top: 3px;
      padding: 7px 9px; border: 1px solid #d9c9b0; border-radius: 8px;
      background: #fff; color: #2b2024;
    }
    input:focus { outline: 2px solid #b8893b; outline-offset: 1px; }
    .evaluar {
      font: inherit; font-size: 15px; font-weight: 600; width: 100%;
      margin-top: 16px; padding: 11px; border: 0; border-radius: 10px;
      background: #6b1f2e; color: #fff; cursor: pointer;
    }
    .evaluar:hover { background: #4a1420; }
    .evaluar:disabled { opacity: .6; cursor: wait; }
    .resultado { margin-top: 16px; }
    .tarjeta { background: #faf5ec; border-radius: 12px; padding: 14px 16px; }
    .rotulo { font-size: 12px; color: #7a6a63; margin: 0; }
    .calidad {
      font-family: "Playfair Display", Georgia, serif; font-size: 30px;
      font-weight: 600; margin: 0 0 10px; text-transform: capitalize;
    }
    .baja { color: #b5523b; } .media { color: #a0762b; } .alta { color: #5d7a3a; }
    .fila { display: grid; grid-template-columns: 52px 1fr 44px; gap: 8px;
            align-items: center; font-size: 12.5px; margin-top: 5px; }
    .fila span:last-child { text-align: right; }
    .barra { height: 8px; background: #eadfcd; border-radius: 99px; overflow: hidden; }
    .relleno { height: 100%; border-radius: 99px; transition: width .4s ease; }
    .relleno.baja { background: #b5523b; }
    .relleno.media { background: #b8893b; }
    .relleno.alta { background: #5d7a3a; }
    .pie { font-size: 11px; color: #9a8a82; margin: 10px 0 0; }
    .error {
      background: #fbeeea; color: #8a2f1c; border-radius: 10px;
      padding: 10px 12px; font-size: 13px; line-height: 1.45;
    }
    @media (max-width: 360px) { .campos { grid-template-columns: 1fr; } }
  `;

  // Crea un elemento HTML con su clase y su texto
  function crear(etiqueta, clase, texto) {
    const elemento = document.createElement(etiqueta);
    if (clase) elemento.className = clase;
    if (texto) elemento.textContent = texto;
    return elemento;
  }

  // Escribe un número como se acostumbra en castellano: 3,21
  function enCastellano(numero) {
    return numero.toLocaleString("es-AR", { maximumFractionDigits: 5 });
  }

  // Hace un pedido a la API con la clave y devuelve el JSON de la respuesta.
  // Si algo sale mal, lanza un error con un mensaje listo para mostrar.
  async function pedir(ruta, opciones) {
    let respuesta;
    try {
      respuesta = await fetch(API + ruta, {
        ...opciones,
        headers: { "Content-Type": "application/json", "X-API-Key": CLAVE },
      });
    } catch (falla) {
      // fetch falla sin respuesta cuando el servicio está caído o cuando
      // este sitio no figura en la lista de CORS de la API
      throw new Error("No se pudo conectar con el servicio. Intente más tarde.");
    }

    const datos = await respuesta.json();
    if (respuesta.ok) return datos;

    if (respuesta.status === 422) {
      const problemas = datos.detalle.map(function (problema) {
        return problema.campo + ": " + problema.mensaje;
      });
      throw new Error("Revise los valores. " + problemas.join(" "));
    }
    throw new Error(datos.mensaje || "El servicio devolvió un error.");
  }

  // --- Estructura fija del widget ---
  const anfitrion = crear("div");
  guion.insertAdjacentElement("afterend", anfitrion);
  const raiz = anfitrion.attachShadow({ mode: "open" });

  const estilos = crear("style");
  estilos.textContent = ESTILOS;
  const caja = crear("div", "caja");
  caja.append(
    crear("p", "marca", "Catador virtual"),
    crear("h2", "", "¿Qué calidad tiene este vino?"),
    crear("p", "bajada",
      "Elija un vino de ejemplo o cargue sus mediciones de laboratorio.")
  );
  const formulario = crear("form");
  formulario.noValidate = true;  // la validación la hace la API
  const resultado = crear("div", "resultado");
  resultado.setAttribute("aria-live", "polite");
  caja.append(formulario, resultado);
  raiz.append(estilos, caja);

  const entradas = {};  // nombre de la variable -> su <input>

  function mostrarError(mensaje) {
    resultado.replaceChildren(crear("div", "error", mensaje));
  }

  function cargarValores(valores) {
    for (const nombre in entradas) {
      entradas[nombre].value = valores[nombre];
    }
  }

  // Arma el formulario a partir de los metadatos que publica la API:
  // si el modelo cambia de variables, el widget se adapta sin tocar el código
  function armarFormulario(info) {
    const ejemplos = crear("div", "ejemplos");
    info.ejemplos.forEach(function (ejemplo) {
      const boton = crear("button", "ejemplo", ejemplo.nombre);
      boton.type = "button";
      boton.addEventListener("click", function () {
        cargarValores(ejemplo.valores);
        ejemplos.querySelectorAll(".ejemplo").forEach(function (otro) {
          otro.classList.toggle("activo", otro === boton);
        });
      });
      ejemplos.append(boton);
    });

    const ajustes = crear("details");
    ajustes.append(crear("summary", "", "Ajustar las mediciones"));
    let grupoActual = "";
    let campos;
    info.variables.forEach(function (variable) {
      if (variable.grupo !== grupoActual) {
        grupoActual = variable.grupo;
        campos = crear("div", "campos");
        ajustes.append(crear("p", "grupo", grupoActual), campos);
      }
      let texto = variable.etiqueta;
      if (variable.unidad) texto += " (" + variable.unidad + ")";
      const etiqueta = crear("label", "", texto);
      const entrada = crear("input");
      entrada.type = "number";
      entrada.step = "any";
      entrada.name = variable.nombre;
      entrada.value = variable.mediana;
      entrada.title = "Valores habituales: " + enCastellano(variable.minimo) +
        " a " + enCastellano(variable.maximo);
      etiqueta.append(entrada);
      campos.append(etiqueta);
      entradas[variable.nombre] = entrada;
    });

    const evaluar = crear("button", "evaluar", "Evaluar vino");
    evaluar.type = "submit";
    formulario.append(ejemplos, ajustes, evaluar);

    formulario.addEventListener("submit", async function (evento) {
      evento.preventDefault();  // evita que la página se recargue
      const vino = {};
      for (const nombre in entradas) {
        vino[nombre] = entradas[nombre].value === ""
          ? null : Number(entradas[nombre].value);
      }
      evaluar.disabled = true;
      evaluar.textContent = "Evaluando...";
      try {
        const prediccion = await pedir("/v1/predict", {
          method: "POST",
          body: JSON.stringify(vino),
        });
        mostrarResultado(prediccion, info.clases);
      } catch (falla) {
        mostrarError(falla.message);
      }
      evaluar.disabled = false;
      evaluar.textContent = "Evaluar vino";
    });
  }

  function mostrarResultado(prediccion, clases) {
    const tarjeta = crear("div", "tarjeta");
    tarjeta.append(
      crear("p", "rotulo", "Calidad estimada"),
      crear("p", "calidad " + prediccion.calidad, prediccion.calidad)
    );
    clases.forEach(function (clase) {
      const porcentaje = Math.round(prediccion.probabilidades[clase] * 100);
      const fila = crear("div", "fila");
      const barra = crear("div", "barra");
      const relleno = crear("div", "relleno " + clase);
      relleno.style.width = porcentaje + "%";
      barra.append(relleno);
      fila.append(crear("span", "", clase), barra,
                  crear("span", "", porcentaje + " %"));
      tarjeta.append(fila);
    });
    tarjeta.append(crear("p", "pie",
      "Estimación de un modelo estadístico, versión " +
      prediccion.version_modelo + ". No reemplaza una cata."));
    resultado.replaceChildren(tarjeta);
  }

  // --- Inicio: pedir los metadatos y dibujar el formulario ---
  if (!API || !CLAVE) {
    mostrarError("Faltan los atributos data-api y data-clave en la etiqueta " +
      "<script> del widget.");
    return;
  }
  pedir("/v1/model-info", { method: "GET" })
    .then(armarFormulario)
    .catch(function (falla) { mostrarError(falla.message); });
})();
