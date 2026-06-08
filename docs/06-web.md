# 06 — Interfaz Web

## 6.1 Descripción general

La interfaz web de Aguacatia es una aplicación server-side desarrollada en Python con los frameworks Jinja2 (plantillas HTML) y HTMX (interacciones AJAX sin JavaScript framework pesado). El servidor ejecuta FastAPI como runtime y expone dos rutas principales: el clasificador y el historial.

- **Framework backend:** FastAPI (Python 3.11)
- **Motor de plantillas:** Jinja2 2.x
- **Librería interactividad:** HTMX 1.9.12
- **Estilos:** CSS custom con variables (dark theme, paleta zinc + colores semafóricos)
- **URL producción:** `https://aguacatia.warlockcode.com`

---

## 6.2 Arquitectura del frontend

La arquitectura es deliberadamente simple: no hay bundler, no hay framework JavaScript, no hay paso de compilación. El servidor renderiza HTML completo para cada ruta, y HTMX reemplaza fragmentos específicos del DOM para las interacciones dinámicas.

```
web/
├── app.py              # FastAPI — rutas GET / y GET /historial, POST /clasificar
├── templates/
│   ├── base.html       # Layout compartido (nav + footer)
│   ├── index.html      # Página principal — formulario de clasificación
│   ├── resultado.html  # Fragmento HTMX — resultado de clasificación
│   └── historial.html  # Página historial paginado
├── static/
│   └── style.css       # Estilos globales (~267 líneas)
└── Dockerfile
```

---

## 6.3 Páginas y flujo del usuario

### Página principal (`/`)

La página de inicio presenta tres secciones:

1. **Hero:** título y subtítulo que explican la funcionalidad del sistema
2. **Formulario de subida:** zona de drag & drop para cargar una imagen JPG/PNG/WEBP
3. **Timeline de etapas:** representación visual horizontal de las 5 etapas de maduración

**Flujo de clasificación:**

| Paso | Acción | Mecanismo |
|------|--------|-----------|
| 1 | Usuario arrastra imagen o hace clic en "selecciona" | JavaScript `FileReader` + `DataTransfer` |
| 2 | Preview de la imagen aparece en la zona de carga | `FileReader.readAsDataURL()` |
| 3 | Botón "Clasificar aguacate" se habilita | `submitBtn.disabled = false` |
| 4 | Usuario hace clic en "Clasificar aguacate" | `<form hx-post="/clasificar">` |
| 5 | HTMX envía POST con `multipart/form-data` | HTMX 1.9.12 |
| 6 | Spinner de carga aparece | `hx-indicator="#loading"` con `.htmx-indicator` CSS |
| 7 | El servidor clasifica la imagen y retorna HTML | `resultado.html` renderizado con Jinja2 |
| 8 | HTMX reemplaza `#result-area` con el resultado | `hx-target="#result-area"` |

### Resultado de clasificación (fragmento HTMX)

Cuando la clasificación es exitosa, el fragmento muestra:

- **Emoji** representativo de la clase (🟢 verde, 🟡 amarillo, 🟠 naranja, 🟣 morado, 🔴 rojo)
- **Nombre de la clase** con su descripción (ej. "Ripe Second Stage — Punto óptimo")
- **Barra de confianza:** porcentaje con barra visual coloreada según la clase
- **Top 5 probabilidades:** tabla expandible con las 5 clases y sus probabilidades
- **Botón "Clasificar otra foto":** resetea el formulario completo sin recargar la página

### Historial (`/historial`)

Tabla paginada con todas las clasificaciones registradas. Cada entrada muestra:

- Imagen del aguacate (cargada desde MinIO; si no disponible, vacío)
- Emoji de clase
- Nombre de la clase y porcentaje de confianza
- Nombre de usuario y fecha de clasificación

**Filtro por usuario:** parámetro `?usuario=nombre` en la URL. Se preserva en la paginación.

**Paginación:** 20 registros por página. Controles "Anterior / Siguiente" generados por Jinja2.

---

## 6.4 Componentes de diseño

### Dark theme con paleta semafórica

| Elemento | Color / Variable CSS |
|----------|---------------------|
| Fondo principal | `#0a0a0a` (`--bg`) |
| Superficie de tarjetas | `#141414` (`--surface`) |
| Bordes | `#1f1f1f` (`--border`) |
| Texto principal | `#e5e5e5` (`--text`) |
| Texto secundario | `#737373` (`--muted`) |
| Unripe | `#22c55e` (verde) |
| Breaking | `#eab308` (amarillo) |
| Ripe First | `#f97316` (naranja) |
| Ripe Second | `#a855f7` (morado) |
| Overripe | `#ef4444` (rojo) |

### Timeline de etapas de maduración

La sección inferior de la página principal muestra las 5 etapas como una línea de tiempo horizontal. Cada etapa tiene:

- Punto circular coloreado con sombra de brillo del mismo color
- Etiqueta con el nombre de la etapa
- Descripción breve del estado visual
- Etiqueta "óptimo" para Ripe Second Stage

Una línea con gradiente de color (verde → rojo) une todos los puntos visualmente.

---

## 6.5 Variables de entorno

| Variable | Descripción | Valor por defecto |
|----------|-------------|-------------------|
| `API_URL` | URL de la API de clasificación | `https://api.aguacatia.warlockcode.com` |

La web actúa como cliente de la API: reenvía las imágenes del usuario hacia la API y renderiza los resultados. No tiene acceso directo al modelo ni a la base de datos.

---

## 6.6 Dockerfile

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY web/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 5000

CMD ["uvicorn", "web.app:app", "--host", "0.0.0.0", "--port", "5000"]
```

---

## 6.7 Decisiones de diseño

| Decisión | Alternativa descartada | Razón |
|----------|----------------------|-------|
| HTMX + Jinja2 | React / Vue SPA | Sin paso de compilación, sin bundler, sin npm. Apropiado para el scope académico. |
| Dark theme | Light theme | Contrasta mejor con los colores semafóricos de las etapas de maduración |
| Fragmento HTMX para resultado | Redirección a nueva página | El usuario puede clasificar múltiples fotos sin perder el contexto de la página |
| Sin framework CSS (Tailwind, Bootstrap) | Tailwind / Bootstrap | CSS custom permite control total con menos de 300 líneas. Sin dependencia de CDN adicional. |
| Drag & drop nativo + FileReader | Librería de uploader | Sin dependencias de terceros. `DataTransfer API` es soporte universal en navegadores modernos. |
