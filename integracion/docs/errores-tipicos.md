# Errores típicos

Ordenados según el momento en que suelen aparecer. Ante cualquier problema, lo primero es mirar dos lugares: la **terminal** donde corre el servicio (o `docker compose logs api`) y la **consola del navegador** (F12, pestañas Consola y Red).

## Al levantar los servicios

| Síntoma | Causa y solución |
|:--|:--|
| `RuntimeError: Falta la variable de entorno API_KEY` | No existe el archivo `.env` o está en otra carpeta. Copie `.env.example` como `.env` dentro de `integracion`. |
| `No such file or directory: ... modelo.joblib` | Falta entrenar el modelo. Ejecute `python modelo/entrenar.py`. Con Docker no hace falta: se entrena al construir la imagen. |
| `ModuleNotFoundError: No module named 'app'` | `uvicorn` se ejecutó desde otra carpeta. Hay que estar en `integracion/api`. |
| `Address already in use` o `port is already allocated` | Otro programa usa ese puerto. Ciérrelo, o cambie el número de la izquierda en `ports` del `docker-compose.yml`, por ejemplo `"8010:8000"`. |
| `env file .env not found` al usar Compose | Falta copiar `.env.example` como `.env`. |
| `InconsistentVersionWarning` al cargar el modelo | El modelo se guardó con otra versión de scikit-learn. Vuelva a entrenar con las versiones de `requirements.txt`. |

## Al consultar la API

| Síntoma | Causa y solución |
|:--|:--|
| `401` aunque se envía la clave | El encabezado se llama `X-API-Key`. Verifique el nombre y que la clave coincida con la del `.env`. Si cambió el `.env`, reinicie la API: las variables se leen al arrancar. |
| `403` en `/v1/predict/batch` | Se está usando la clave pública. El lote necesita la privada. |
| `422` | Algún dato falta, no es un número o está fuera de rango. El campo `detalle` de la respuesta indica cuál. |
| `429` | Se superó el tope de pedidos por minuto de la clave pública. |
| `404` | La ruta no existe. Recuerde el prefijo `/v1`. |

## En el widget

| Síntoma | Causa y solución |
|:--|:--|
| "No se pudo conectar con el servicio" y la consola indica un error de CORS | El origen de la página no figura en `ORIGENES_PERMITIDOS`. Tiene que coincidir exactamente: protocolo, dominio y puerto, sin barra final. |
| El mismo mensaje, y la consola indica `ERR_CONNECTION_REFUSED` | La API no está levantada o `data-api` apunta a otra dirección. |
| "Faltan los atributos data-api y data-clave" | La etiqueta `<script>` no tiene esos atributos. |
| Al abrir la página con doble clic, el widget muestra "No se pudo conectar con el servicio" | La página se abrió como archivo (`file://`) y no tiene un origen que la API pueda autorizar. Sírvala con `python -m http.server 8080`. |
| Funciona en `localhost` pero no una vez publicado | La API sigue autorizando solo `http://localhost:8080`, o `data-api` todavía apunta a `localhost`. |
| Una página con HTTPS no puede llamar a una API con HTTP | El navegador bloquea ese contenido mixto. La API desplegada también tiene que usar HTTPS. |

## En la aplicación Flask

| Síntoma | Causa y solución |
|:--|:--|
| "No se pudo conectar con la API del modelo" | La API no está levantada o `API_URL` es incorrecta. Dentro de Compose, la API se encuentra por el nombre del servicio (`http://api:8000`), no por `localhost`. |
| "La API respondió con el código 401" | La variable `API_KEY` de Flask no coincide con la de la API. |
| Al enviar el formulario se recarga toda la página | No se cargó HTMX. Revise la conexión y la etiqueta `<script>` de `base.html`. |
| El CSV indica que faltan columnas | Los nombres del encabezado no coinciden con los de las variables. Descargue el CSV de ejemplo desde la pantalla **Un lote**. |
| "No se pudo leer el archivo" | El archivo no está en UTF-8. En Excel, elija **CSV UTF-8** al guardar. |
| Un error señala `fila 5, ph` | Es la fila 5 de la planilla, contando el encabezado como fila 1. |

## En la pantalla Conversar

| Síntoma | Causa y solución |
|:--|:--|
| "Este escenario no está activo" | Falta `ANTHROPIC_API_KEY` en el archivo `.env`. Después de agregarla hay que volver a levantar la aplicación Flask: las variables se leen al arrancar. |
| "La clave del modelo de lenguaje no es válida" | La clave está mal copiada, fue revocada o pertenece a otro proveedor. |
| "El modelo de lenguaje recibió demasiados pedidos" | Se alcanzó el tope de uso de la cuenta del proveedor. |
| La respuesta tarda varios segundos | Es esperable: cada respuesta implica una o más llamadas al modelo de lenguaje y a la API de vinos. |
| La respuesta no usó el modelo de vinos | Debajo de la respuesta no aparece la línea "Consultó el modelo de vinos". Reformule la pregunta con las mediciones del vino. |

## En la aplicación Next.js

| Síntoma | Causa y solución |
|:--|:--|
| "No pudimos consultar el modelo" | La API no está levantada, falta el archivo `.env.local` en `fronts/nextjs` o su `API_KEY` no coincide con la de la API. Después de cambiar el archivo, reinicie `npm run dev`. |
| La compilación falla con un mensaje sobre `server-only` | Un componente del navegador (con `"use client"`) importa `lib/api.ts`. Ese archivo solo puede usarse en el servidor: el pedido tiene que pasar por el Route Handler. |
| TypeScript marca errores después de cambiar la API | Los tipos quedaron viejos. Con la API levantada, ejecute `npm run tipos` y corrija lo que el editor señale. |
| Un campo muestra el error apenas se escribe y el pedido no sale | Es la validación del navegador. Los rangos de `lib/esquema.ts` tienen que coincidir con los de la API. |
| `npm install` falla o advierte por la versión de Node.js | Next.js necesita Node.js 20.9 o posterior. |

## En el script de automatización

| Síntoma | Causa y solución |
|:--|:--|
| "No hay planillas para evaluar" | La carpeta `automatizacion/entrada` está vacía. |
| "No se pudo completar la evaluación: la API respondió 401" | El script no encontró la clave. Lee el mismo archivo `.env` que la API. |
| `KeyError` con el nombre de una medición | A la planilla le falta esa columna. |
| La tarea programada "no hace nada" | Revise el código de salida y lo que el script escribe por pantalla: ante un error termina con código 1 y explica el motivo. |

## Al desplegar

| Síntoma | Causa y solución |
|:--|:--|
| La construcción falla con `COPY failed` o no encuentra `modelo/` | El contexto de construcción es incorrecto. Para la API tiene que ser `./integracion`. |
| El servicio queda en estado de falla después de construir | Falta alguna variable de entorno. Revise la pestaña de registros de la plataforma. |
| El primer pedido tarda cerca de un minuto | El plan gratuito apagó el servicio por falta de uso. Los pedidos siguientes responden normalmente. |
| En Vercel, la aplicación compila pero muestra "No pudimos consultar el modelo" | Faltan `API_URL` o `API_KEY` en las variables del proyecto, o la API está apagada por falta de uso. Después de cargar las variables hay que volver a desplegar. |
| Las pruebas de latencia fallan contra el servicio desplegado | La red agrega demora. Ajuste los máximos con `LATENCIA_PROMEDIO_MS` y `LATENCIA_P95_MS`. |

---

Contexto: [Guía de integración](https://jumafernandez.github.io/eda-isft189/guia-integracion.html) - [Guía de FastAPI](https://jumafernandez.github.io/eda-isft189/guia-fastapi.html) - [Guía de Dockerfile](https://jumafernandez.github.io/eda-isft189/guia-dockerfile.html). En CRISP-DM corresponde a la fase de Despliegue; acompaña el trabajo del entregable [04].
