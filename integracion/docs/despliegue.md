# Despliegue

Desplegar es poner la solución en una máquina encendida de manera permanente y con una dirección pública. Para el entregable [04] alcanza con que funcione de manera local; el despliegue en un entorno accesible se valora, pero no es obligatorio.

## Plataforma administrada o servidor propio

En la clase C03 (Infraestructura tecnológica) se comparó la infraestructura propia (*on-premise*) con la nube. La misma decisión aparece al desplegar un modelo, en una escala más chica:

| | Plataforma administrada | Servidor propio |
|:--|:--|:--|
| Ejemplos | Render (API y Flask), Vercel (Next.js) | Una máquina virtual con Docker Compose y nginx como proxy inverso |
| Qué se entrega | El repositorio. La plataforma construye la imagen y la publica. | Los contenedores, que uno mismo instala y mantiene. |
| Control | Limitado a las opciones de la plataforma. | Total: sistema operativo, red, versiones. |
| Costo | Plan gratuito con límites; después se paga por uso. | El de la máquina, se use o no. |
| Mantenimiento | A cargo de la plataforma. | A cargo propio: actualizaciones, reinicios, copias de respaldo. |
| Disponibilidad | La garantiza la plataforma. En el plan gratuito, el servicio se apaga si no recibe pedidos. | Depende de la máquina y de quien la cuida. |
| HTTPS y dominio | Incluidos. | Hay que configurarlos. |
| Quién se ocupa de qué | El equipo, del código y las variables. La plataforma, del resto. | El equipo, de todo. |
| En términos de la clase C03 | Nube, en la modalidad de plataforma como servicio. | Más cerca de *on-premise*: la responsabilidad es propia. |

Para un proyecto de la cursada, la plataforma administrada es el camino más corto. El servidor propio tiene sentido cuando la institución ya tiene una máquina disponible, cuando los datos no pueden salir de ella o cuando se quiere aprender a administrarla; el procedimiento está en [servidor-propio.md](servidor-propio.md).

## Antes de desplegar

1. El proyecto está en un repositorio de GitHub y **no** incluye el archivo `.env`.
2. Las pruebas pasan contra la API local: `pytest tests -v`.
3. Tiene decididas las claves de producción, distintas de las de desarrollo. Para generar una:

```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

## Desplegar la API en Render

[Render](https://render.com) construye la imagen a partir del `Dockerfile` del repositorio y la publica con HTTPS.

1. Cree una cuenta en Render e ingrese con su usuario de GitHub.
2. Elija **New > Web Service** y seleccione el repositorio.
3. Complete el formulario:

| Campo | Valor |
|:--|:--|
| Language | Docker |
| Root Directory | (vacío) |
| Dockerfile Path | `./integracion/api/Dockerfile` |
| Docker Build Context Directory | `./integracion` |
| Instance Type | Free |
| Health Check Path | `/v1/health` |

4. En **Environment Variables**, cargue:

| Variable | Valor |
|:--|:--|
| `API_KEY` | La clave privada de producción. |
| `API_KEY_PUBLICA` | La clave pública de producción. |
| `ORIGENES_PERMITIDOS` | La dirección pública del sitio que aloja el widget, sin barra final. Por ejemplo `https://usuario.github.io`. |
| `FORWARDED_ALLOW_IPS` | `*` |

5. Presione **Create Web Service**. La primera construcción tarda varios minutos, porque instala las librerías y entrena el modelo.
6. Cuando el estado pase a **Live**, la API queda publicada en una dirección del tipo `https://api-vinos.onrender.com`. Compruébela:

```bash
API_KEY=la-clave-privada python tests/probar_api.py https://api-vinos.onrender.com
```

Dos aclaraciones:

- El contexto de construcción es `integracion` y no `integracion/api` porque la imagen necesita dos carpetas hermanas: `modelo/` y `api/`.
- `FORWARDED_ALLOW_IPS` le indica a uvicorn que confíe en el dato de dirección IP que le pasa el proxy de Render. Sin esa variable, todos los visitantes parecerían llegar desde la misma IP y compartirían el tope de pedidos.

### Atajo: el archivo `render.yaml`

En la raíz del repositorio hay un archivo `render.yaml` que describe los servicios (un *blueprint*). Con **New > Blueprint**, Render lo lee, crea la API y la aplicación Flask, genera las claves y solo pregunta por los valores que no puede deducir.

## Desplegar la aplicación Flask en Render

Se repite el procedimiento con otro servicio web:

| Campo | Valor |
|:--|:--|
| Language | Docker |
| Dockerfile Path | `./integracion/fronts/flask/Dockerfile` |
| Docker Build Context Directory | `./integracion/fronts/flask` |
| Instance Type | Free |

| Variable | Valor |
|:--|:--|
| `API_URL` | La dirección pública de la API, sin barra final. |
| `API_KEY` | La misma clave privada que se cargó en la API. |
| `ANTHROPIC_API_KEY` | Opcional. Activa la pantalla **Conversar**. Lea antes el punto 11 de [seguridad.md](seguridad.md): publicada sin un tope de uso, cualquiera puede gastar con su clave. |

La aplicación Flask no se agrega a `ORIGENES_PERMITIDOS`: quien llama a la API es su servidor, no un navegador.

## Desplegar la aplicación Next.js en Vercel

[Vercel](https://vercel.com) es la plataforma de la empresa que desarrolla Next.js. Compila el proyecto por su cuenta, sin usar el `Dockerfile`.

1. Cree una cuenta en Vercel e ingrese con su usuario de GitHub.
2. Elija **Add New > Project** e importe el repositorio.
3. En **Root Directory**, seleccione `integracion/fronts/nextjs`. Vercel detecta que es un proyecto Next.js.
4. En **Environment Variables**, cargue:

| Variable | Valor |
|:--|:--|
| `API_URL` | La dirección pública de la API, sin barra final. |
| `API_KEY` | La misma clave privada que se cargó en la API. |

5. Presione **Deploy**. Al terminar, la aplicación queda en una dirección del tipo `https://catador.vercel.app`.

A partir de ese momento, cada cambio que se sube a la rama principal del repositorio se vuelve a desplegar solo. Igual que Flask, esta aplicación no se agrega a `ORIGENES_PERMITIDOS`: quien llama a la API es el servidor de Next.js.

## Publicar el widget

El widget son dos archivos estáticos (`widget.js` y la página que lo usa), así que se puede publicar en cualquier servicio de páginas estáticas, como GitHub Pages. Antes de publicarlo:

1. En la etiqueta `<script>`, cambie `data-api` por la dirección pública de la API y `data-clave` por la clave **pública** de producción.
2. Agregue el origen del sitio a `ORIGENES_PERMITIDOS` en la API.

## Después de desplegar

- Corra `probar_api.py` y las pruebas con `BASE_URL` apuntando a la dirección pública.
- Abra cada cliente desde otra computadora o desde el teléfono.
- En el plan gratuito, Render apaga los servicios que pasan unos 15 minutos sin recibir pedidos. El primer pedido posterior tarda cerca de un minuto. Antes de una demostración, abra la aplicación con anticipación.
- Los registros de cada servicio se consultan en la pestaña **Logs** del panel.

---

Contexto: [Guía de integración](https://jumafernandez.github.io/eda-isft189/guia-integracion.html) - [Guía de FastAPI](https://jumafernandez.github.io/eda-isft189/guia-fastapi.html) - [Guía de Dockerfile](https://jumafernandez.github.io/eda-isft189/guia-dockerfile.html). En CRISP-DM corresponde a la fase de Despliegue y cubre el punto de despliegue que valora el entregable [04].
