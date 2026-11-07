# AGROCONTROL - Contexto del Proyecto

## 🏗️ Stack Tecnológico
- **Backend**: Python con Flask, Flask-CORS, SQLite3.
- **Frontend**: Vue 3 (Composition API con `<script setup lang="ts">`), TypeScript, Element Plus, Vue Router.
- **Base de Datos**: SQLite (`lotes` y `cultivos`).

## ⚙️ Reglas de Base de Datos y Backend
- **Restricciones (CHECK constraints)**: La columna `etapa` en la tabla `cultivos` **solo acepta valores en minúsculas**: `germinacion`, `vegetativa`, `floracion`, `fructificacion`, `cosecha`.
- **Conectividad**: El backend corre en `http://127.0.0.1:5000` y el frontend en `http://localhost:5173`. Las peticiones usan JSON y CORS está habilitado.

## 📝 Estándares de Código y Estilo
- Tipar estrictamente con interfaces en TypeScript (ej. `Lote`, `Cultivo`).
- Usar bloques `try-catch` en las peticiones `fetch` y notificaciones con `ElMessage` de Element Plus.
- Al modificar componentes de Vue o scripts de Flask, preferir mostrar fragmentos de código precisos en lugar de archivos completos para agilizar el desarrollo.