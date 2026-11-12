# Apéndice: desplegar en un servidor propio

Este apéndice es opcional. Describe cómo publicar la solución en una máquina que administra el propio equipo, por ejemplo una máquina virtual de la institución o de un proveedor de nube, con Docker Compose y nginx como proxy inverso. La comparación con una plataforma administrada está en [despliegue.md](despliegue.md).

## Qué cambia respecto de la computadora personal

En su computadora, cada servicio publica un puerto (`8000`, `8001`, `8080`) y se accede por `localhost`. En un servidor conviene que el único punto de entrada sea un **proxy inverso**: un programa que recibe todos los pedidos en los puertos 80 y 443 y los reparte al contenedor que corresponde según el dominio o la ruta. El proxy también se ocupa de HTTPS. Los contenedores dejan de estar expuestos directamente a internet.

```text
Internet -> nginx (puertos 80 y 443, HTTPS)
              |- api.midominio.edu.ar -> contenedor api (8000)
              |- app.midominio.edu.ar -> contenedor flask (8001)
```

## Requisitos

- Una máquina con Linux, accesible por SSH, con Docker y el complemento Compose instalados.
- Un dominio o subdominio que apunte a la dirección IP de la máquina.
- Los puertos 80 y 443 abiertos en el cortafuegos.

## Pasos

1. Clone el repositorio en el servidor y cree el archivo `.env` con las claves de producción. El archivo se escribe a mano en el servidor; no viaja por el repositorio.

```bash
git clone https://github.com/usuario/proyecto.git
cd proyecto/integracion
cp .env.example .env
nano .env
```

2. Publique los puertos solo hacia la propia máquina, para que el único acceso desde afuera sea nginx. En `docker-compose.yml`, anteponga `127.0.0.1:` al puerto de cada servicio:

```yaml
    ports:
      - "127.0.0.1:8000:8000"
```

3. Levante los servicios en segundo plano:

```bash
docker compose up --build -d
docker compose ps
```

4. Instale nginx y cree un archivo de configuración por dominio, por ejemplo `/etc/nginx/sites-available/api`:

```nginx
server {
    server_name api.midominio.edu.ar;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

5. Active el sitio y pida el certificado de HTTPS con Certbot, que además lo renueva de manera automática:

```bash
sudo ln -s /etc/nginx/sites-available/api /etc/nginx/sites-enabled/
sudo nginx -t && sudo systemctl reload nginx
sudo certbot --nginx -d api.midominio.edu.ar
```

6. Compruebe el servicio desde su computadora:

```bash
API_KEY=la-clave-privada python tests/probar_api.py https://api.midominio.edu.ar
```

## Lo que queda a cargo del equipo

En una plataforma administrada estas tareas no existen; en un servidor propio, alguien tiene que hacerlas:

- Actualizar el sistema operativo y Docker.
- Reconstruir y reiniciar los servicios cuando cambia el código: `git pull && docker compose up --build -d`.
- Asegurar que los servicios vuelvan a levantarse si la máquina se reinicia (opción `restart: unless-stopped` en cada servicio de Compose).
- Revisar los registros (`docker compose logs -f api`) y el espacio en disco.
- Resguardar el archivo `.env` y renovar las claves si se filtran.

---

Contexto: [Guía de integración](https://jumafernandez.github.io/eda-isft189/guia-integracion.html) - [Guía de FastAPI](https://jumafernandez.github.io/eda-isft189/guia-fastapi.html) - [Guía de Dockerfile](https://jumafernandez.github.io/eda-isft189/guia-dockerfile.html). En CRISP-DM corresponde a la fase de Despliegue; es una alternativa para el despliegue que valora el entregable [04].
