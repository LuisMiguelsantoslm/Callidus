# 🗂️ CFS1 Pro — Servidor y Cliente de Archivos Remoto

> Un explorador de archivos remoto escrito en **Python puro** (sin dependencias externas) con interfaz gráfica moderna en Tkinter, protocolo binario propio con compresión, autenticación por token y transferencias cancelables.

![Python](https://img.shields.io/badge/python-3.8%2B-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20Linux%20%7C%20macOS-lightgrey.svg)
![No Dependencies](https://img.shields.io/badge/dependencies-none-success.svg)

---

## ✨ Características

### 🌐 Protocolo
- **Framing binario propio** (`MAGIC + versión + flags + longitud`) sobre TCP.
- **Compresión zlib** automática en mensajes de control > 256 bytes.
- **Autenticación SHA-256** con token de sesión aleatorio (`secrets.token_hex`).
- **Anti brute-force**: bloqueo temporal por IP tras N intentos fallidos.
- **Heartbeat (ping/pong)** para detectar desconexiones.
- **Chunks de 256 KB** con lectura/escritura exacta.

### 🖥️ Cliente (Tkinter)
- **Interfaz oscura** estilo VS Code con `ttk` (sin dependencias externas).
- **Navegación completa**: Atrás / Adelante / Subir / Refrescar + **historial**.
- **Breadcrumb clickable** para saltar a cualquier nivel de la ruta.
- **Sidebar con accesos rápidos**: Unidades + Escritorio, Documentos, Imágenes, Música, Vídeos, Descargas.
- **Búsqueda en vivo** con contador de resultados filtrados.
- **Ordenamiento por columna** (clic en la cabecera, indicador ▲▼).
- **Iconos según extensión** (imagen, vídeo, audio, código, comprimido, etc.).
- **Menú contextual** (clic derecho): Descargar, Renombrar, Eliminar, Copiar ruta.
- **Barra de progreso** con % / velocidad / ETA y botón **Cancelar**.
- **Panel de estadísticas** del servidor en tiempo real.
- **Persistencia de ajustes** en `~/.cfs1_pro.json`.

### 📦 Transferencias
- **Subida y descarga de archivos** individuales.
- **Descarga recursiva de carpetas** preservando estructura (con manifest + streaming).
- **Resolución automática de colisiones**: `archivo (1).ext`, `archivo (2).ext`, ...
- **Cancelables** desde el cliente en cualquier momento.
- **Cálculo de velocidad y ETA** en tiempo real.

### 🛡️ Seguridad (del lado servidor)
- **Path traversal** bloqueado (`../`, rutas absolutas, cambios de unidad).
- **Filtro de archivos de sistema** en la raíz (`System Volume Information`, `$RECYCLE.BIN`, etc.).
- **Confirmación interactiva** antes de compartir una unidad completa.
- **Protección contra borrado de la raíz** compartida.
- **Sesiones con token** — cada comando tras el login requiere el token.

---

## 📸 Capturas

> *(Añade aquí capturas de pantalla del cliente funcionando)*
> 
> ```
> ┌───────────────────────────────────────────────────────────┐
> │  🗂️  CFS1 Pro    ● Conectado        ⏱ 12m · 📄 12,483 · 👥 2  │
> ├───────────────────────────────────────────────────────────┤
> │  Host: [callidus.servehttp.com]  Puerto: [7771]  ●●●●●●●●  │
> ├───────────────────────────────────────────────────────────┤
> │  ◀ ▶ ▲ ⟳ │ ⬇ Descargar  ⬆ Subir  📁 Nueva carpeta  📊 Stats │
> ├──────────┬────────────────────────────────────────────────┤
> │ EQUIPO   │  📂 C:\ › Users › L.M › Documents              │
> │ 💽 C:    │  ┌───────────────────────────────────────────┐ │
> │ 💽 D:    │  │ 📁 Proyectos           —     2025-01-15   │ │
> │          │  │ 📄 informe.pdf      2.4 MB   2025-01-14   │ │
> │ RÁPIDO   │  │ 🖼️ foto.jpg        840 KB   2025-01-12   │ │
> │ 🏠 Inicio │  └───────────────────────────────────────────┘ │
> │ 📄 Docs  │                                                │
> │ 🖼️ Pics  │                                                │
> └──────────┴────────────────────────────────────────────────┘
> ```

---

## 🚀 Instalación

### Requisitos

- **Python 3.8 o superior** (funciona con 3.10, 3.11, 3.12, 3.13, 3.14)
- **Tkinter** (viene con Python en Windows y macOS; en Linux puede requerir `python3-tk`)
- **No requiere `pip install`** — todo es biblioteca estándar.

### Verificar Tkinter

```bash
python -c "import tkinter; print('Tkinter OK')"
