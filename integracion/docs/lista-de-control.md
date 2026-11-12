# Lista de control para la presentación del 19/11

Entregable **[04] Despliegue del modelo y presentación de la solución**. La lista separa lo que la consigna pide, lo que valora y lo que va más allá, para que cada equipo decida dónde poner el esfuerzo.

## 1. Lo que pide el entregable

- [ ] Hay un **servicio** que expone el modelo.
- [ ] El servicio tiene **entradas y salidas definidas**: se sabe qué datos recibe, de qué tipo, y qué devuelve.
- [ ] El servicio funciona de manera **local**, en la computadora del equipo.
- [ ] Hay una **interfaz** que consume ese servicio.
- [ ] La interfaz representa un **caso de uso concreto** del proyecto: se puede decir quién la usa, en qué momento y para decidir qué.

## 2. Lo que se valora

- [ ] El código está **organizado** y se puede recorrer sin ayuda.
- [ ] La **lógica del modelo** está separada de la **capa de servicio**.
- [ ] Hay **manejo de errores**: se sabe qué ve la persona si carga un dato inválido o si el servicio no responde.
- [ ] La interfaz consume el modelo **a través de la API**, sin cargar el archivo del modelo por su cuenta.
- [ ] La solución está **desplegada** en un entorno accesible desde otra computadora.

## 3. Lo que va más allá de la consigna

- [ ] La API pide una clave y la clave no está escrita en el código.
- [ ] CORS autoriza una lista de orígenes.
- [ ] Hay pruebas automáticas del contrato de la API.
- [ ] Las pruebas corren solas ante cada cambio (integración continua).
- [ ] La API informa los metadatos del modelo: versión, variables y métricas.

## 4. La presentación

Dura entre 7 y 10 minutos e incluye una demostración en vivo.

- [ ] Está claro el recorrido: problema, modelo, solución desplegada, demostración.
- [ ] Se explica qué forma de uso del modelo se eligió (consulta individual, lote, sitio ajeno, exploración, de sistema a sistema, conversación) y por qué.
- [ ] Se explican las decisiones de arquitectura: quién llama a la API y por qué.
- [ ] La demostración se ensayó completa, en la computadora y la red que se van a usar.
- [ ] Si la solución está en un plan gratuito, se abre unos minutos antes para que el servicio esté encendido.
- [ ] Hay un respaldo por si falla la conexión: capturas de pantalla o un video corto.
- [ ] La demostración incluye un caso con error, además del caso que sale bien.

## 5. Revisión rápida antes de presentar

```bash
docker compose up --build            # ¿levanta desde cero?
python tests/probar_api.py           # ¿la API cumple su contrato?
```

- [ ] El proyecto levanta en una computadora distinta de la que se usó para desarrollarlo.
- [ ] El archivo `.env` no está en el repositorio.
- [ ] El repositorio explica cómo levantar la solución.

---

Contexto: [Guía de integración](https://jumafernandez.github.io/eda-isft189/guia-integracion.html) - [Guía de FastAPI](https://jumafernandez.github.io/eda-isft189/guia-fastapi.html) - [Guía de Dockerfile](https://jumafernandez.github.io/eda-isft189/guia-dockerfile.html). En CRISP-DM, el entregable [04] corresponde a la fase de Despliegue.
