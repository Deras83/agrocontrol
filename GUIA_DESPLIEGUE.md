# Guía de despliegue y cambios — AgroControl
Siempre en la raíz del proyecto. Abre Docker Desktop y espera a que el motor esté corriendo.
1. Enciendes la PC
cd C:\Users\jdera\Desktop\IIIPAC2026\paradigmas\proyecto\agrocontrol_project\agrocontrol_project
docker compose up -d
docker compose ps
Cuando ps diga Up, abre http://localhost:8080 o en el teléfono http://192.168.1.108:8080.
Si Docker Desktop arranca solo al iniciar sesión, el contenedor puede levantarse por su cuenta; up -d es inofensivo, solo confirma que esté corriendo.
2. Quieres que Docker deje de correr (PC encendida)
docker compose down
3. Vas a apagar la PC
No necesitas nada: el contenedor se detiene junto con Windows. (Si quieres, puedes ejecutar docker compose down antes; da igual.)
4. Vuelves a encender la PC
Igual que el paso 1:
docker compose up -d
docker compose ps
Solo si cambiaste código
docker compose up -d --build
Los datos de tu base no se pierden al hacer down ni al apagar la PC.
## Resumen

La app quedó preparada para correr como **un solo servicio** (Flask sirve la API y el
frontend compilado). Se agregó Docker para levantarla localmente y configuración para
desplegarla en Fly.io.

- **Local (Docker):** `http://localhost:8080` y desde el teléfono `http://<IP-de-tu-PC>:8080`.
- **Base de datos:** el contenedor usa **tu** `database/agrocontrol.db` (no una copia).
- **Sin `npm run dev` ni `python app.py`** cuando uses Docker.
- **Fly.io:** no tiene capa gratis; tiene prueba de $1 y luego factura. Con una sola
  máquina de 512 MB + 1 GB de volumen el total ronda **$3.8/mes**, y Fly **exonera**
  facturas personales menores a **$5/mes** (ver sección Fly.io).

Todos los comandos se ejecutan en **PowerShell** y en la **raíz del proyecto**:

```
C:\Users\jdera\Desktop\IIIPAC2026\paradigmas\proyecto\agrocontrol_project\agrocontrol_project
```

---

## 1. Cambios realizados en el proyecto

### Archivos nuevos

| Archivo | Para qué |
|---|---|
| `Dockerfile` | Imagen multi-stage: compila Vue con Node y arma el backend con Python + SWI-Prolog + Gunicorn. |
| `.dockerignore` | Evita copiar `.git`, `node_modules`, `dist`, `__pycache__` y `.db` a la imagen. |
| `docker-compose.yml` | Levanta el contenedor en el puerto `8080` y monta tu base real. |
| `fly.toml` | Configuración de despliegue en Fly.io (1 máquina, volumen `/data`, auto-seed apagado). |

### Archivos modificados

| Archivo | Cambio |
|---|---|
| `app.py` | Sirve el build de Vue (`agrocontrol-frontend/dist`) y hace fallback a `index.html` para las rutas del router. Al arrancar crea las tablas y solo siembra datos de ejemplo si la BD está vacía. |
| `config.py` | `DB_PATH` se puede sobrescribir con la variable `AGROCONTROL_DB_PATH` (en Docker apunta a `/data/agrocontrol.db`). |
| `requirements.txt` | Se agregó `gunicorn` (servidor de producción). |
| `agrocontrol-frontend/vite.config.ts` | Proxy `/api` → `http://127.0.0.1:5000` para que funcione en desarrollo y desde el teléfono. |
| `agrocontrol-frontend/src/main.ts` | Se eliminó el interceptor de `fetch` que reescribía `127.0.0.1` (ya no hace falta: todo usa rutas relativas). |
| `agrocontrol-frontend/src/views/*.vue` | Las URLs `http://127.0.0.1:5000/api/...` ahora son `/api/...` en: `AplicacionesView`, `BitacoraView`, `CosechasView`, `CultivosView`, `DashboardView`, `DiagnosticosView`, `FincasView`, `InsumosView`, `PrologView`, `ReporteView`. |

### Respaldo de la base de datos

Se creó una copia de seguridad antes de tocar nada:

```
database\agrocontrol.db.2026-11-20.bak
```

---

## 2. Cómo funciona la base de datos en Docker

En `docker-compose.yml`:

```yaml
volumes:
  - ./database/agrocontrol.db:/data/agrocontrol.db
environment:
  AGROCONTROL_DB_PATH: /data/agrocontrol.db
  AGROCONTROL_AUTO_SEED: "0"
```

Esto significa:

- El contenedor **lee y escribe tu archivo real** `database\agrocontrol.db`.
- Lo que registres desde la web queda guardado al instante en ese archivo.
- El auto-seed está **apagado**, así que nunca sobrescribe tus datos.
- **No ejecutes el backend local y Docker al mismo tiempo**: ambos abren el mismo
  archivo SQLite y pueden bloquearse.

---

## 3. Uso diario con Docker (lo normal)

### Primera vez o después de cambiar código

```powershell
docker compose up -d --build
```

Cuándo usarlo:
- La primera vez.
- Cada vez que modifiques **código** (Python, Vue, TypeScript, CSS).
- Si cambiaste `Dockerfile`, `docker-compose.yml`, `requirements.txt` o `package.json`.

### Solo encender (sin cambios de código)

```powershell
docker compose up -d
```

Cuándo usarlo:
- Después de reiniciar la PC.
- Después de un `docker compose down`.

### Ver estado / logs

```powershell
docker compose ps          # ¿está corriendo?
docker compose logs -f     # ver errores en vivo (Ctrl+C para salir)
```

### Apagar

```powershell
docker compose down
```

Apaga y elimina el contenedor, pero **no borra** tu base (es tu archivo real).

### Reiniciar sin reconstruir

```powershell
docker compose restart
```

### Abrir en la PC

```
http://localhost:8080
```

### Abrir desde el teléfono

1. PC y teléfono en la **misma red Wi-Fi**.
2. Obtener la IP de la PC:

   ```powershell
   ipconfig
   ```

   Busca la IPv4 de tu adaptador Wi-Fi (por ejemplo `192.168.1.108`).
3. Abrir en el teléfono:

   ```
   http://192.168.1.108:8080
   ```

Si no carga:
- Verifica que Docker Desktop esté abierto y `docker compose ps` diga `Up`.
- Permite **Docker Desktop** en el Firewall de Windows (redes privadas).
- La IP puede cambiar al reconectarte al Wi-Fi; vuelve a ejecutar `ipconfig`.

---

## 4. Que el contenedor arranque solo

1. Docker Desktop → **Settings → General** → activar
   **"Start Docker Desktop when you sign in"**.
2. El compose ya tiene `restart: unless-stopped`, así que al iniciar Docker el
   contenedor vuelve a levantarse.

Además, para que la app esté disponible desde el teléfono, la PC debe estar:
- Encendida y sin hibernar.
- Conectada al Wi-Fi.
- Con Docker Desktop abierto.

Sugerencia: Configuración de Windows → Sistema → Energía → Suspensión = **Nunca**
(conectado a corriente).

---

## 5. Modo desarrollo (opcional, con recarga automática)

Úsalo solo cuando estés programando y **con Docker apagado** (`docker compose down`).

Terminal 1 (raíz del proyecto):

```powershell
python app.py
```

Terminal 2 (carpeta del frontend):

```powershell
cd agrocontrol-frontend
npm run dev -- --host
```

Esto también funciona desde el teléfono gracias al proxy `/api` agregado en Vite.
Cuando termines, cierra ambos y vuelve a `docker compose up -d --build`.

---

## 6. Fly.io

### ¿Es gratis?

**No hay capa gratis.** Desde octubre de 2024 Fly.io cobra por uso:

- Cuenta nueva: **$1 de crédito por 7 días**, sin tarjeta.
- Después: se requiere tarjeta.
- Si la factura mensual de tu organización personal es **menor a $5**, Fly la **exonera**
  (queda en $0).

Costo estimado de este proyecto con **una** máquina:

| Recurso | Precio |
|---|---|
| Máquina `shared-cpu-1x` 512 MB, encendida 24/7 | ~$3.69/mes |
| Volumen 1 GB | ~$0.15/mes |
| Tráfico de salida (10 GB) | ~$0.20/mes |
| **Total** | **~$4.04/mes → exonerado (< $5)** |

> Importante: `fly deploy` crea **2 máquinas** por defecto (alta disponibilidad) y eso
> duplicaría el costo. Usa siempre `--ha=false` para una sola máquina. Además, SQLite
> no debe compartirse entre varias máquinas.

### Requisito previo

Instalar `flyctl` (PowerShell):

```powershell
iwr https://fly.io/install.ps1 -useb | iex
```

Cerrar y abrir PowerShell, y verificar:

```powershell
fly version
```

### Primera vez

1. Crear cuenta / iniciar sesión:

   ```powershell
   fly auth signup
   # o si ya tienes cuenta:
   fly auth login
   ```

2. Elegir un nombre de app **único** y editar la primera línea de `fly.toml`:

   ```toml
   app = "agrocontrol-tu-nombre"
   ```

3. Registrar la app:

   ```powershell
   fly apps create agrocontrol-tu-nombre
   ```

4. Crear el volumen en la **misma región** de `fly.toml` (`mia`):

   ```powershell
   fly volumes create agrocontrol_data --region mia --size 1
   ```

5. Desplegar (una sola máquina):

   ```powershell
   fly deploy --ha=false
   ```

6. Abrir la app:

   ```powershell
   fly open
   ```

   La URL será `https://agrocontrol-tu-nombre.fly.dev`.

### Subir tu base de datos real a Fly

El primer despliegue deja la BD vacía (sin seed). Luego subes tu archivo:

```powershell
fly sftp put database\agrocontrol.db /data/agrocontrol.db
fly apps restart agrocontrol-tu-nombre
```

Verificar que quedó la data real:

```powershell
fly logs
```

Debe responder la API con tus datos (`/api/lotes`, `/api/bitacora`, etc.).

### Actualizar después de cambiar código

```powershell
fly deploy --ha=false
```

### Comandos útiles de Fly

```powershell
fly status                  # estado de la app
fly logs                    # logs en vivo
fly open                    # abrir la URL
fly apps restart <nombre>   # reiniciar
fly volumes list            # ver volúmenes
```

> Nota: en Fly los cambios de código **sí** requieren `fly deploy`. Los datos que
> registres en la web se guardan en el volumen `/data` y sobreviven a los despliegues.

---



## 7. Resumen de comandos (referencia rápida)

| Situación | Comando | Dónde |
|---|---|---|
| Primera vez / cambio de código | `docker compose up -d --build` | Raíz del proyecto |
| Solo encender | `docker compose up -d` | Raíz del proyecto |
| Ver estado | `docker compose ps` | Raíz del proyecto |
| Ver logs | `docker compose logs -f` | Raíz del proyecto |
| Apagar | `docker compose down` | Raíz del proyecto |
| Desarrollo backend | `python app.py` | Raíz del proyecto |
| Desarrollo frontend | `npm run dev -- --host` | `agrocontrol-frontend` |
| Desplegar en Fly | `fly deploy --ha=false` | Raíz del proyecto |
| Subir BD a Fly | `fly sftp put database\agrocontrol.db /data/agrocontrol.db` | Raíz del proyecto |

---

## 8. Problemas comunes

| Síntoma | Causa / solución |
|---|---|
| `http://localhost:8080` no carga | Docker Desktop cerrado o contenedor detenido. Revisa `docker compose ps`. |
| Desde el teléfono no carga | IP equivocada, firewall bloqueando, o PC/teléfono en redes distintas. |
| Cambié código y no se refleja | Falta reconstruir: `docker compose up -d --build`. |
| `database is locked` | Backend local y Docker usando la misma BD a la vez. Apaga uno. |
| El teléfono deja de funcionar de un día a otro | La IP de la PC cambió. Ejecuta `ipconfig` y usa la nueva. |
| Fly no arranca | Falta el volumen o el nombre no coincide con `fly.toml`. Revisa `fly logs`. |
| Fly creó 2 máquinas | Redesplega con `fly deploy --ha=false` y destruye la máquina sobrante. |

---

## 9. Despliegue gratis: Supabase (base de datos) + Render (app)

### Cómo elige el motor de base de datos

- **Sin** `DATABASE_URL` → SQLite local (menú, pruebas y Docker de siempre).
- **Con** `DATABASE_URL` → PostgreSQL en Supabase.

No hay que cambiar las consultas: el adaptador traduce los marcadores `?` a `%s`.

### 1. Crear la base en Supabase

1. Entra a https://supabase.com → **New project** (guarda la contraseña).
2. **Project Settings → Database → Connection string → Connection pooling
   (Transaction)**, puerto **6543**.
3. Copia la URI `postgresql://...` y añade `?sslmode=require` si no viene.

### 2. Desplegar en Render

1. El código ya está en GitHub.
2. Render → **New → Blueprint** → conecta el repo (usa `render.yaml`).
3. En la variable `DATABASE_URL` pega la URI de Supabase (marcada como secreto).
4. **Deploy**. La primera vez crea las tablas y siembra datos de ejemplo.

### Notas

- La app escucha el puerto que Render inyecta por la variable `PORT`.
- Render Free se duerme a los 15 min sin tráfico; el primer acceso tarda ~1 min.
- Supabase Free (500 MB) se pausa tras 1 semana sin actividad.
- Para migrar tus datos actuales de SQLite a Supabase, pide un script de migración.

---

## 10. Pruebas automáticas de todos los endpoints (GitHub Actions)

El workflow `.github/workflows/smoke.yml` prueba la API en cada push (sin login, sin
tocar tu base de producción). Usa `tests/smoke_api.py`:

- **Local (CI):** crea una BD SQLite temporal, siembra datos y prueba **todos** los
  endpoints: lecturas, escrituras, borrados, validaciones y los 3 diagnósticos de Prolog.
- **Remoto (opcional):** si defines la variable de repositorio `SMOKE_BASE_URL`
  (Settings → Secrets and variables → Actions → Variables), además prueba tu app de
  Render (solo lecturas y diagnósticos, sin borrados).

Ejecutarlo a mano:

```powershell
python tests\smoke_api.py
python tests\smoke_api.py --base-url https://tu-app.onrender.com
```

También puedes lanzarlo desde GitHub: **Actions → Smoke API → Run workflow** (campo
`base_url` opcional).
