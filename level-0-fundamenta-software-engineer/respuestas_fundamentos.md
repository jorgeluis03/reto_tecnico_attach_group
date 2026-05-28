# Fundamentos de Ingeniería de Software

## 1. Tecnología para reproducir entornos locales y garantizar la consistencia entre desarrollo y producción

La herramienta que uso para esto es **Docker**, junto con **Docker Compose** para orquestar múltiples servicios.

En mi experiencia en Rimac Seguros (Softtek), los repositorios más modernos ya vienen con un `docker-compose.yml` que permite levantar localmente todo lo que la aplicación necesita (base de datos, Redis, etc.), de manera que todos los desarrolladores del equipo trabajan con el mismo entorno. Otros repositorios más legacy se levantan con Serverless Framework en modo offline o directamente con AWS SDK, pero la tendencia ha sido migrar hacia Docker.

Lo que garantiza la consistencia es que la misma imagen Docker que construyo en mi máquina local es la que pasa por el pipeline de Azure DevOps y la que termina corriendo en producción. Las variables de entorno sensibles se gestionan con AWS SSM Parameter Store y Secrets Manager, y localmente se replican con archivos `.env`.

---

## 2. Herramientas de gestión de paquetes de Python

**pip** — Es la herramienta que he usado desde el inicio. Todos los proyectos en producción en Rimac (backends FastAPI, agentes con Google ADK) usan `pip` con `requirements.txt`. También lo usé en mis proyectos personales como Legalizate y la plataforma GovTech.

**uv** — Lo adopté más recientemente cuando empecé a trabajar en múltiples repositorios en paralelo que requerían versiones distintas de Python (uno en 3.9, otro en 3.11, otro en 3.12). `uv` me permite cambiar de versión de Python de forma ágil, similar a como `nvm` funciona para Node.js.

**venv** — Siempre trabajo con entornos virtuales para aislar las dependencias de cada proyecto. Es una práctica básica pero fundamental cuando manejas muchos repos simultáneamente.

---

## 3. Lenguajes de programación con experiencia

**Python** — Mi lenguaje principal, llevo aproximadamente 4 años trabajándolo en producción. Lo uso para desarrollo de agentes de IA con Google ADK, arquitecturas RAG con LangChain/LangGraph, backends con FastAPI, y desarrollo de MCPs personalizados. Proyectos destacados: un copilot de solo consulta para brokers de Rimac (consulta de pólizas, cotizaciones), agentes de migración de bases de datos, el proyecto Legalizate (asistente legal con RAG, +1970 páginas indexadas), y la plataforma GovTech ganadora en PUCP.

**JavaScript / TypeScript** — La mayoría de repositorios backend en Rimac están en JavaScript (Node.js/Express), y los más modernos en TypeScript (NestJS). Es mi segundo lenguaje de uso diario. En frontend he trabajado con ReactJs cuando ha sido necesario.

**Bash** — Lo uso constantemente para automatización: scripts para clonar masivamente 60+ repositorios, automatizar tareas repetitivas según la demanda del trabajo, y en el uso diario de la terminal (grep, find, manejo de procesos, etc.).

**Java** — Tengo conocimientos de Java con Spring Boot de mi formación, aunque en los últimos años no lo he aplicado en un proyecto productivo.

---

## 4. Herramientas de IaC (Infrastructure as Code)

**Serverless Framework** — Es la herramienta de IaC que más he usado. En Rimac Seguros la utilizamos para definir y desplegar Lambdas, API Gateways, DynamoDB y demás recursos AWS. La estructura típica incluye un `serverless.yml` general, y archivos separados `functions.cloud.yml` y `functions.local.yml` para las definiciones de funciones. Un aprendizaje importante: no poner todas las variables de entorno en el `serverless.yml` global porque se propagan a todas las Lambdas y pueden exceder el límite de 4KB de AWS. Lo correcto es definir las variables específicas de cada Lambda en sus archivos de funciones.

**Docker Compose** — Lo conozco y puedo configurarlo para definir infraestructura local de forma declarativa. Lo he visto en varios proyectos y entiendo su funcionamiento como herramienta de definición de infraestructura.

**AWS CDK** — Lo he visto en proyectos del equipo como herramienta para definir infraestructura como código en TypeScript.

**Terraform** — Lo vi en dos proyectos, conozco su sintaxis HCL pero no he sido yo quien lo configure directamente.

---

## 5. Pasos para construir una aplicación monolítica en una VM con Docker y Docker Compose

Stack: **FastAPI + PostgreSQL + Redis + Nginx**

Elijo PostgreSQL porque ofrece mejor soporte de tipos JSON nativos, extensiones útiles para búsqueda de texto, y es el estándar más adoptado para aplicaciones nuevas en producción.

### Paso 1: Preparar la VM

Conectarse por SSH a la VM, actualizar paquetes del sistema e instalar Docker:

```bash
ssh -i mi-llave.pem usuario@ip-de-la-vm
sudo apt update && sudo apt upgrade -y
sudo apt install -y docker.io docker-compose-v2
sudo usermod -aG docker $USER
```

Configurar el firewall para exponer solo lo necesario:

```bash
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw allow 22/tcp
sudo ufw enable
```

### Paso 2: Estructura del proyecto

```
monolith/
├── docker-compose.yml
├── .env
├── app/
│   ├── Dockerfile
│   ├── main.py
│   └── requirements.txt
└── nginx/
    └── nginx.conf
```

### Paso 3: Dockerfile de la app FastAPI

```dockerfile
FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Paso 4: Configurar Nginx como reverse proxy

```nginx
upstream fastapi_app {
    server app:8000;
}

server {
    listen 80;
    server_name _;

    location / {
        proxy_pass http://fastapi_app;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}
```

### Paso 5: Docker Compose para orquestar todo

```yaml
services:
  app:
    build: ./app
    env_file: .env
    depends_on:
      db:
        condition: service_healthy
      redis:
        condition: service_started
    networks:
      - internal

  db:
    image: postgres:16-alpine
    environment:
      POSTGRES_DB: ${DB_NAME}
      POSTGRES_USER: ${DB_USER}
      POSTGRES_PASSWORD: ${DB_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${DB_USER}"]
      interval: 5s
      timeout: 3s
      retries: 5
    networks:
      - internal

  redis:
    image: redis:7-alpine
    volumes:
      - redis_data:/data
    networks:
      - internal

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/conf.d/default.conf
    depends_on:
      - app
    networks:
      - internal

volumes:
  postgres_data:
  redis_data:

networks:
  internal:
    driver: bridge
```

### Paso 6: Definir variables de entorno en `.env`

```
DB_NAME=myapp
DB_USER=appuser
DB_PASSWORD=secure_password_here
DB_HOST=db
DB_PORT=5432
REDIS_URL=redis://redis:6379/0
```

### Paso 7: Desplegar y verificar

```bash
git clone <repo-url> && cd monolith
cp .env.example .env && nano .env
docker compose up -d --build
docker compose ps
curl http://localhost/health
```

**Puntos importantes:**

- Los contenedores se comunican entre sí por nombre de servicio (la app se conecta a la BD usando `host=db`), Docker Compose crea la red interna automáticamente.
- Los volúmenes (`postgres_data`, `redis_data`) persisten la data aunque se destruyan los contenedores.
- El `healthcheck` en PostgreSQL evita que la app intente conectarse antes de que la BD esté lista.
- Solo Nginx expone puertos al exterior (80), los demás servicios quedan en la red interna.

---

## 6. Comandos de shell del día a día

**Navegación y archivos:** `cd`, `ls`, `pwd`, `mkdir -p`, `rm -rf`, `cp`, `mv`, `cat`, `tail -f` (para seguir logs en tiempo real).

**Búsqueda:** `grep -r "pattern" ./src/` para buscar texto en código, `grep -rn` cuando necesito el número de línea, `find . -name "*.py"` para localizar archivos por extensión. Muy útiles cuando necesito verificar la existencia de archivos o encontrar similitudes en una larga lista de archivos.

**Procesos y puertos:** `netstat -tlnp | grep :3000` o `lsof -i :8000` para identificar qué proceso ocupa un puerto, `ps aux | grep node` para buscar procesos, `kill -9 <PID>` para matarlos. Esto lo uso frecuentemente cuando hay conflictos de puertos al levantar servicios localmente.

**Git (uso avanzado):**

- Lo básico: `git status`, `git diff`, `git add`, `git commit`, `git push`, `git pull`
- `git pull --rebase origin main` para mantener historial limpio
- `git stash` / `git stash pop` para guardar cambios temporalmente
- `git rebase -i HEAD~3` para reescribir o squashear commits
- `git cherry-pick <hash>` para traer commits específicos de otra rama
- `git log --oneline --graph` para visualizar el historial
- `git reflog` para recuperar commits que creía perdidos
- `git reset --soft HEAD~1` para deshacer el último commit sin perder cambios
- `git add -p` para stage interactivo por hunks

**Docker:** `docker compose up -d --build`, `docker compose down`, `docker ps`, `docker logs -f`, `docker exec -it <container> bash`.

**Networking:** `curl` lo uso mucho para testear APIs localmente, especialmente cuando quiero automatizar requests en secuencia. `wget` para descargar archivos.

**Scripting Bash:** Escribo scripts `.sh` para automatizar tareas repetitivas. El ejemplo más claro: un script para clonar masivamente los 60+ repositorios del equipo en Rimac, que lee una lista de URLs y los clona (o actualiza si ya existen). También scripts para ejecutar comandos en múltiples repos simultáneamente o automatizar secuencias de requests HTTP con curl.

**Package managers:** `npm install`, `npm run dev`, `nvm use 18`/`nvm use 20` para cambiar versiones de Node; `pip install -r requirements.txt`, `uv python install 3.12` para Python.

---

## 7. ¿Por qué y cuándo abriría el puerto 22 en una VM en la nube?

El puerto 22 es el puerto de **SSH (Secure Shell)**, el protocolo que permite conectarse remotamente a una máquina de forma cifrada.

**¿Cuándo abrirlo?**

- Para la configuración inicial de la VM: instalar software, configurar servicios, desplegar la aplicación por primera vez.
- Para troubleshooting cuando necesitas acceder directamente a la máquina y los logs o monitoreo remoto no son suficientes.
- Para transferir archivos con `scp` o `sftp`.

**Buenas prácticas de seguridad:**

- Nunca dejarlo abierto a todo internet (`0.0.0.0/0`). Siempre restringir por IP de origen en el Security Group.
- Usar autenticación por par de llaves SSH, nunca por contraseña.
- Preferir alternativas más seguras cuando sea posible: AWS SSM Session Manager permite acceder a la instancia sin abrir el puerto 22. Bastion hosts o VPN corporativa también son opciones válidas.
- Cerrar el puerto una vez que ya no se necesite.

**En mi contexto en Rimac Seguros:** Por políticas de seguridad corporativa (industria de seguros), no tengo permisos para acceder directamente por SSH a las VMs productivas. La administración se realiza mediante herramientas gestionadas y pipelines CI/CD, con permisos limitados por roles. Esto es la práctica correcta en entornos empresariales de alta seguridad.
