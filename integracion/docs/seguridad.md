# Seguridad básica

Un servicio que sale de la computadora propia queda al alcance de cualquiera que conozca su dirección. Esta lista reúne las precauciones mínimas que aplica el ejemplo y dónde se ve cada una en el código. No convierte al servicio en un sistema seguro frente a un ataque dirigido; evita los descuidos más comunes.

## 1. Los secretos no van en el código ni en el repositorio

- Las claves se leen de variables de entorno (`api/app/config.py`).
- El archivo `.env` figura en `.gitignore`. Lo que se sube es `.env.example`, con valores de muestra.
- Si una clave llegó al repositorio, borrarla en un commit posterior no alcanza: queda en el historial. Hay que **cambiarla** por una nueva.

## 2. Claves distintas para desarrollo y producción

Las claves de `.env.example` son públicas, porque están en el repositorio. Al desplegar se generan claves nuevas y se cargan en el panel de la plataforma:

```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

## 3. Lo que llega al navegador es público

Cualquier persona puede ver el código de una página y los pedidos que hace, con las herramientas de desarrollo del navegador (F12). Por eso:

- La clave **privada** solo la usan servidores (las aplicaciones Flask y Next.js) y nunca se escribe en HTML ni en el JavaScript que recibe el navegador. En Next.js, el archivo que la usa (`lib/api.ts`) empieza con `import "server-only"`, que hace fallar la compilación si se lo importa desde el navegador.
- El widget usa una clave **pública** con permisos mínimos: no puede predecir por lote y tiene un tope de pedidos por minuto (`api/app/seguridad.py`).

## 4. CORS con lista de orígenes

`ORIGENES_PERMITIDOS` enumera los sitios que pueden consultar la API desde un navegador. Se evita `*`, que autoriza a cualquiera.

CORS no reemplaza a la clave: es una regla que aplican los navegadores. `curl`, Python u otro servidor la ignoran.

## 5. Validar siempre en el servidor

La API valida el tipo y el rango de cada dato con Pydantic (`api/app/esquemas.py`) y limita el tamaño de los lotes. La validación en el navegador mejora la experiencia de uso, pero se puede saltear; la del servidor, no. La aplicación Flask limita además el tamaño del archivo que acepta, y la de Next.js vuelve a validar en su Route Handler.

## 6. Los errores no revelan detalles internos

Ante una falla inesperada, la API responde un mensaje general y anota el detalle en su registro (`api/app/errores.py`). Una traza de error mostrada al público le da a un atacante información sobre librerías, rutas y versiones.

## 7. El registro no guarda secretos

Se anotan el método, la ruta, el código de respuesta y la demora de cada pedido. No se anotan las claves ni el contenido de los pedidos.

## 8. Contenedores sin privilegios

Los `Dockerfile` crean un usuario común y ejecutan el servicio con él. Si alguien logra ejecutar código dentro del contenedor, no tiene permisos de administrador.

## 9. HTTPS

Con HTTP, la clave viaja como texto legible para cualquiera que esté en el camino. Las plataformas administradas publican con HTTPS de manera automática; en un servidor propio hay que configurarlo ([servidor-propio.md](servidor-propio.md)).

## 10. Librerías con versión fija

Los `requirements.txt` fijan la versión de cada librería. Así el servicio desplegado usa exactamente lo que se probó, y una actualización se hace de manera deliberada.

## 11. El escenario conversacional

La pantalla **Conversar** usa un modelo de lenguaje externo, y eso agrega consideraciones propias:

- **La clave del proveedor es un secreto más.** Va en `ANTHROPIC_API_KEY`, se lee en el servidor y nunca llega al navegador.
- **Cada mensaje cuesta dinero.** La aplicación acota el largo de cada mensaje y la cantidad de mensajes previos que reenvía, pero no limita cuántos pedidos hace una persona. Antes de publicarla hay que agregar un tope de uso o un inicio de sesión, y fijar un límite de gasto en la cuenta del proveedor.
- **Lo que se escribe sale del entorno propio.** Los mensajes viajan al proveedor del modelo de lenguaje. No deben incluir datos personales ni reservados.
- **Las herramientas marcan el límite.** El modelo de lenguaje solo puede pedir dos operaciones de consulta, que no modifican nada. Si alguien intenta manipularlo con el texto que escribe, lo máximo que obtiene es una predicción. Una herramienta que escribiera o borrara datos exigiría controles adicionales.
- **La conversación llega desde el navegador.** El servidor no confía en ella: acepta solo mensajes de texto con los roles válidos (`leer_historial` en `app.py`).
- **Trazabilidad.** Las estimaciones salen siempre del modelo de vinos, y la pantalla muestra qué se consultó y con qué datos.

## Lo que este ejemplo no cubre

- Usuarios y contraseñas: una clave identifica a una aplicación, no a una persona.
- Un tope de pedidos que resista varios procesos o reinicios: el del ejemplo vive en memoria.
- Protección frente a ataques de saturación, que suele delegarse en la plataforma o en un servicio especializado.

Para profundizar: [OWASP API Security Top 10](https://owasp.org/API-Security/).

---

Contexto: [Guía de integración](https://jumafernandez.github.io/eda-isft189/guia-integracion.html) - [Guía de FastAPI](https://jumafernandez.github.io/eda-isft189/guia-fastapi.html) - [Guía de Dockerfile](https://jumafernandez.github.io/eda-isft189/guia-dockerfile.html). En CRISP-DM corresponde a la fase de Despliegue; va más allá de lo que pide el entregable [04].
