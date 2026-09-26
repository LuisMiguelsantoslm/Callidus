# 🗂️ Callidus — Servidor y Cliente de Archivos Remoto

**Creado por [Luis Miguel Santos](https://github.com/LuisMiguelsantoslm)** · `LuisMiguelsantoslm`

<p align="center">
  <img src="https://img.shields.io/badge/python-3.8%2B-blue.svg" alt="Python">
  <img src="https://img.shields.io/badge/license-MIT-green.svg" alt="License">
  <img src="https://img.shields.io/badge/platform-Windows%20%7C%20Linux%20%7C%20macOS-lightgrey.svg" alt="Platform">
  <img src="https://img.shields.io/badge/dependencies-none-success.svg" alt="No deps">
  <img src="https://img.shields.io/badge/purpose-educational-orange.svg" alt="Educational">
  <img src="https://img.shields.io/badge/author-LuisMiguelsantoslm-blueviolet.svg" alt="Author">
  <img src="https://img.shields.io/badge/protocol-CFS1-informational.svg" alt="Protocol">
</p>

> **Callidus** es un explorador de archivos remoto hecho en **Python puro** con interfaz gráfica moderna en Tkinter, protocolo binario propio (CFS1), autenticación por token, transferencias cancelables y descarga recursiva de carpetas.

**Protocolo interno:** CFS1 (Callidus File Server v1)
**Repositorio:** [github.com/LuisMiguelsantoslm/Callidus](https://github.com/LuisMiguelsantoslm/Callidus)

> ### 🌟 ¿Por qué "Callidus"?
>
> Del latín ***callidus***: **astuto, hábil, ingenioso**. Un nombre que refleja la filosofía del proyecto — hacer más con menos, usando únicamente la biblioteca estándar de Python para construir un explorador remoto completo y profesional.

---

## 📖 Tabla de contenidos

- [⚠️ Aviso educativo](#️-aviso-educativo)
- [✨ ¿Qué es Callidus?](#-qué-es-callidus)
- [👤 Autor](#-autor)
- [🎯 Características](#-características)
- [🔑 Credenciales por defecto](#-credenciales-por-defecto)
- [🧩 Dependencias](#-dependencias)
- [🚀 Instalación](#-instalación)
- [🏁 Uso rápido](#-uso-rápido)
- [🌐 Acceso desde Internet (No-IP + Port Forwarding)](#-acceso-desde-internet-no-ip--port-forwarding)
- [🖥️ Ejecución automática al iniciar Windows](#️-ejecución-automática-al-iniciar-windows)
- [⌨️ Atajos de teclado](#️-atajos-de-teclado)
- [⚙️ Configuración avanzada](#️-configuración-avanzada)
- [🔐 Seguridad](#-seguridad)
- [🏗️ Arquitectura del protocolo CFS1](#️-arquitectura-del-protocolo-cfs1)
- [📁 Estructura del proyecto](#-estructura-del-proyecto)
- [🛠️ Roadmap](#️-roadmap)
- [🤝 Contribuir](#-contribuir)
- [📜 Licencia](#-licencia)
- [📞 Contacto](#-contacto)

---

## ⚠️ Aviso educativo

Este proyecto fue creado **con fines estrictamente educativos** y de aprendizaje. Su objetivo es que estudiantes, autodidactas y desarrolladores curiosos puedan:

- 🎓 **Aprender cómo funciona un protocolo binario sobre TCP**: framing, cabeceras, flags, compresión.
- 🎓 **Entender la autenticación con hashing** (SHA-256) y tokens de sesión.
- 🎓 **Practicar concurrencia en Python** con `threading` y colas seguras (`queue.Queue`).
- 🎓 **Ver cómo se construye una GUI en Tkinter** de nivel profesional sin frameworks externos.
- 🎓 **Comprender la transferencia de archivos por bloques** (chunks) con progreso, velocidad y ETA.
- 🎓 **Aprender conceptos de redes**: NAT, port forwarding, DNS dinámico, túneles SSH.

### ❗ Uso responsable

- **NO** lo uses para acceder a archivos de terceros sin su consentimiento explícito.
- **NO** compartas la raíz `C:\` de una máquina con datos sensibles en producción.
- **NO** lo expongas a Internet sin antes leer la sección [Seguridad](#-seguridad).
- El autor no se responsabiliza del mal uso que se haga de esta herramienta.
- Se recomienda practicar **solo en tu red local (LAN)** o entre máquinas de tu propiedad.

---

## ✨ ¿Qué es Callidus?

**Callidus** (del latín *"astuto, hábil, ingenioso"*) es un sistema cliente-servidor que te permite explorar y transferir archivos entre dos computadoras a través de la red, como si fuera un mini "Google Drive" casero o un "TeamViewer de archivos".

Está compuesto por dos programas:

| Programa | Rol | Qué hace |
|---|---|---|
| `server.py` | Se ejecuta en la PC que **comparte** los archivos | Escucha en un puerto TCP, autentica clientes y sirve archivos |
| `client.py` | Se ejecuta en la PC que **accede** a los archivos | Interfaz gráfica para navegar, descargar, subir y gestionar |

Ambos se comunican usando un **protocolo binario propio** llamado **CFS1** (*Callidus File Server v1*), diseñado para ser eficiente, claro y didáctico.

### ¿Por qué el nombre "Callidus"?

- 🏛️ **Raíz latina**: *callidus* significa astuto, hábil, ingenioso.
- 🎯 **Filosofía del proyecto**: hacer más con menos — un explorador remoto completo usando **solo la biblioteca estándar** de Python.
- 🔤 **Coincide con la máquina servidor** del autor (`callidus.servehttp.com`).
- 🚀 **Suena profesional** y no choca con otros proyectos existentes.

---

## 👤 Autor

<table>
  <tr>
    <td><strong>Proyecto</strong></td>
    <td><strong>Callidus</strong></td>
  </tr>
  <tr>
    <td><strong>Autor</strong></td>
    <td>Luis Miguel Santos</td>
  </tr>
  <tr>
    <td><strong>Usuario</strong></td>
    <td><code>LuisMiguelsantoslm</code></td>
  </tr>
  <tr>
    <td><strong>GitHub</strong></td>
    <td><a href="https://github.com/LuisMiguelsantoslm">@LuisMiguelsantoslm</a></td>
  </tr>
  <tr>
    <td><strong>Repositorio</strong></td>
    <td><a href="https://github.com/LuisMiguelsantoslm/Callidus">github.com/LuisMiguelsantoslm/Callidus</a></td>
  </tr>
  <tr>
    <td><strong>Protocolo interno</strong></td>
    <td>CFS1 (Callidus File Server v1)</td>
  </tr>
  <tr>
    <td><strong>Propósito</strong></td>
    <td>Educativo / Aprendizaje de redes, protocolos binarios y GUI en Python</td>
  </tr>
</table>

### 🎓 Sobre el proyecto

**Callidus** fue desarrollado por **Luis Miguel Santos** (`LuisMiguelsantoslm`) como parte de su proceso de aprendizaje en **Python, redes y desarrollo de interfaces gráficas**. Nació de la idea de construir desde cero un sistema cliente-servidor sin depender de frameworks externos, entendiendo cada capa: desde los sockets TCP hasta la serialización binaria de mensajes.

Si este proyecto te resultó útil para aprender, considera darle una ⭐ en GitHub.

### 📚 Aprendizajes documentados

A lo largo del desarrollo de Callidus se practicaron y documentaron los siguientes temas:

- 🌐 **Redes**: sockets TCP, framing binario, NAT, port forwarding, DNS dinámico.
- 🔐 **Seguridad**: hashing con SHA-256, tokens de sesión, anti brute-force, path traversal.
- 🧵 **Concurrencia**: `threading`, `queue.Queue`, comunicación thread-safe con la GUI.
- 🎨 **GUI**: Tkinter avanzado con `ttk`, estilos personalizados, atajos de teclado.
- 📦 **Protocolos**: diseño de comandos, versionado, compatibilidad, compresión zlib.
- 🗂️ **Sistemas de archivos**: `pathlib`, permisos, archivos ocultos, recorrido recursivo.
- 🐍 **Python moderno**: type hints, context managers, f-strings, dataclasses.

---

## 🎯 Características

### 🌐 Protocolo
- **Framing binario propio** (`MAGIC + versión + flags + longitud`) sobre TCP.
- **Compresión zlib** automática en mensajes de control mayores a 256 bytes.
- **Autenticación SHA-256** con token de sesión aleatorio (`secrets.token_hex`).
- **Anti brute-force**: bloqueo temporal por IP tras 5 intentos fallidos.
- **Heartbeat (ping/pong)** cada 20s para detectar desconexiones.
- **Chunks de 256 KB** con lectura/escritura exacta (`recv_exact`).

### 🖥️ Cliente (Tkinter)
- **Interfaz oscura** estilo VS Code.
- **Navegación completa**: Atrás / Adelante / Subir / Refrescar + historial.
- **Breadcrumb clickable** para saltar a cualquier nivel.
- **Sidebar con accesos rápidos**: Unidades + Escritorio, Documentos, Imágenes, Música, Vídeos, Descargas.
- **Búsqueda en vivo** con contador de filtrados.
- **Ordenamiento por columna** (clic en la cabecera).
- **Iconos según extensión** (imagen, vídeo, audio, código, etc.).
- **Menú contextual** (clic derecho): Descargar, Renombrar, Eliminar, Copiar ruta.
- **Barra de progreso** con % / velocidad / ETA y botón Cancelar.
- **Panel de estadísticas** del servidor en tiempo real.

### 📦 Transferencias
- **Subida y descarga de archivos** individuales.
- **Descarga recursiva de carpetas** preservando estructura.
- **Resolución de colisiones**: `archivo (1).ext`, `archivo (2).ext`, ...
- **Cancelables** en cualquier momento con `Esc`.
- **Cálculo de velocidad y ETA** en tiempo real.

---

## 🔑 Credenciales por defecto

> ⚠️ **IMPORTANTE**: Cambia la contraseña antes de exponer el servidor a cualquier red.

| Campo | Valor por defecto |
|---|---|
| **Puerto** | `7771` |
| **Contraseña** | **`admin123`** |
| **Host (local)** | `127.0.0.1` |
| **Host (remoto)** | `callidus.servehttp.com` |

### Cambiar la contraseña

La contraseña **NO se guarda en texto plano** — se guarda como hash SHA-256. Para cambiarla:

**1. Genera el hash de tu nueva contraseña:**

```bash
python -c "import hashlib; print(hashlib.sha256('MiNuevaClaveSegura123'.encode()).hexdigest())"
```

**2. Copia el resultado** (una cadena hexadecimal de 64 caracteres).

**3. Edita `server.py`**, busca esta línea:

```python
PASSWORD_HASH = hashlib.sha256('admin123'.encode()).hexdigest()
```

Y reemplázala por:

```python
PASSWORD_HASH = 'el_hash_que_generaste_aqui'
```

**4. Reinicia el servidor.**

**5. En el cliente**, escribe la contraseña en texto plano (`MiNuevaClaveSegura123`) — se hashea automáticamente antes de enviarla.

---

## 🧩 Dependencias

Callidus **NO requiere `pip install`**. Todo funciona con la **biblioteca estándar** de Python.

### Dependencias por sistema operativo

| Componente | Windows | macOS | Linux |
|---|---|---|---|
| **Python 3.8+** | ✅ Descargar de [python.org](https://www.python.org/downloads/) | ✅ Viene instalado | ✅ `sudo apt install python3` |
| **Tkinter** (GUI) | ✅ Incluido con Python | ✅ Incluido | ⚠️ Requiere instalación |
| **socket, threading, pickle, struct, zlib, hashlib, secrets, queue** | ✅ Incluidos | ✅ Incluidos | ✅ Incluidos |

### Instalar Tkinter en Linux (si no lo tienes)

```bash
# Debian / Ubuntu / Linux Mint
sudo apt update && sudo apt install python3-tk

# Fedora / RHEL / CentOS
sudo dnf install python3-tkinter

# Arch / Manjaro
sudo pacman -S tk

# openSUSE
sudo zypper install python3-tk
```

### Verificar que todo está listo

```bash
python -c "import tkinter, socket, threading, pickle, struct, zlib, hashlib, secrets; print('✅ Todo listo')"
```

Si imprime `✅ Todo listo`, puedes ejecutar Callidus.

### Lista completa de módulos usados

```python
# Biblioteca estándar (no requieren instalación)
import argparse       # parsing de argumentos CLI
import datetime       # timestamps en logs
import hashlib        # SHA-256 para contraseñas
import os             # sistema de archivos
import pickle         # serialización de mensajes
import queue          # cola thread-safe GUI ↔ workers
import secrets        # tokens criptográficamente seguros
import shutil         # borrado recursivo de carpetas
import socket         # comunicación TCP
import string         # detección de unidades Windows
import struct         # empaquetado binario de cabeceras
import sys            # control de salida
import threading      # concurrencia
import time           # timestamps y medición de velocidad
import tkinter        # GUI (se instala con Python en Win/Mac)
import traceback      # debugging de excepciones
import zlib           # compresión de mensajes
from pathlib import Path  # manejo moderno de rutas
```

---

## 🚀 Instalación

### 1. Clonar el repositorio

```bash
git clone https://github.com/LuisMiguelsantoslm/Callidus.git
cd Callidus
```

O simplemente descarga `server.py` y `client.py` y colócalos en la misma carpeta.

### 2. Verificar Python

```bash
python --version
# Debe mostrar Python 3.8.x o superior
```

En Windows, si `python` no funciona, prueba con `py`:
```bash
py --version
```

### 3. Ejecutar

```bash
python server.py   # en la PC que comparte
python client.py   # en la PC que accede
```

---

## 🏁 Uso rápido

### Paso 1 — Iniciar el servidor

En la máquina que compartirá los archivos:

```bash
python server.py
```

Por defecto comparte **la raíz de la unidad** donde esté el script (ej. `C:\`).

Verás un aviso de seguridad:

```
============================================================
  ⚠️  AVISO DE SEGURIDAD
============================================================
  Compartiendo TODA la unidad:  C:\

  Cualquiera con la contraseña podrá leer, escribir y BORRAR
  cualquier archivo de esta unidad.
============================================================
  Escribe "si" para continuar:
```

Escribe `si` y presiona Enter.

Salida esperada:

```
[HH:MM:SS] [SRV] Callidus v2 en 0.0.0.0:7771
[HH:MM:SS] [SRV] Compartiendo: C:\
[HH:MM:SS] [SRV] Ctrl+C para detener
```

### Paso 2 — Iniciar el cliente

En la misma PC o en otra:

```bash
python client.py
```

Rellena:

| Campo | Valor |
|---|---|
| **Host** | `127.0.0.1` (misma PC) o tu IP/DNS (remoto) |
| **Puerto** | `7771` |
| **Contraseña** | `admin123` |

Pulsa **Conectar**. ¡Listo!

---

## 🌐 Acceso desde Internet (No-IP + Port Forwarding)

Esta sección explica paso a paso cómo acceder a tu servidor Callidus **desde cualquier lugar del mundo** usando un DNS dinámico (No-IP) y abriendo el puerto en tu router.

### 📋 Requisitos previos

1. Tu PC servidor debe estar **encendida** y ejecutando `server.py`.
2. Debes tener acceso al **panel de administración de tu router** (usuario/contraseña).
3. Una cuenta gratuita en [No-IP](https://www.noip.com/) o similar.

### 🧩 Paso 1 — Configurar No-IP (DNS dinámico)

**¿Por qué necesito No-IP?**
La mayoría de los proveedores de Internet (ISP) asignan una **IP pública dinámica** que cambia cada cierto tiempo. No-IP te da un nombre fijo (ej. `micasa.ddns.net`) que siempre apunta a tu IP actual.

#### 1.1 Crear cuenta

1. Ve a [https://www.noip.com/sign-up](https://www.noip.com/sign-up)
2. Regístrate (gratis, solo pide email y contraseña).
3. Confirma tu correo.

#### 1.2 Crear un hostname

1. Inicia sesión en No-IP.
2. Menú izquierdo → **Dynamic DNS** → **No-IP Hostnames**.
3. Pulsa **Create Hostname**.
4. Rellena:

| Campo | Ejemplo |
|---|---|
| **Hostname** | `callidus` |
| **Domain** | `servehttp.com` (o `ddns.net`, `hopto.org`, etc.) |
| **Record Type** | `A` |
| **IP Address** | Pulsa **"Use current IP"** (detecta tu IP automáticamente) |

5. Pulsa **Create Hostname**.

Tu dominio quedará así: **`callidus.servehttp.com`** ✅

#### 1.3 Instalar el actualizador de No-IP (DUC)

Como tu IP cambia, necesitas un pequeño programa que actualice No-IP cada vez que cambie:

**Windows / macOS:**

1. Descarga **DUC (Dynamic Update Client)**: [https://www.noip.com/download](https://www.noip.com/download)
2. Instálalo y ejecútalo.
3. Inicia sesión con tu cuenta de No-IP.
4. Selecciona el hostname que creaste.
5. Marca **"Run at startup"** para que se actualice solo al encender la PC.

**Linux (alternativa):**

```bash
sudo apt install noip2
sudo noip2 -C   # configurar
sudo noip2      # iniciar
```

**Alternativa manual (crontab cada 5 min):**

```bash
*/5 * * * * curl "https://dynupdate.no-ip.com/nic/update?hostname=callidus.servehttp.com&myip=$(curl -s ifconfig.me)" -u "tu_usuario:tu_password"
```

#### 1.4 Verificar que funciona

Abre una terminal y ejecuta:

```bash
nslookup callidus.servehttp.com
```

Debe devolver tu **IP pública actual**. Puedes confirmar tu IP real en [https://api.ipify.org](https://api.ipify.org).

Si coinciden → **No-IP está funcionando correctamente** ✅

### 🧩 Paso 2 — Abrir el puerto en el router (Port Forwarding)

**¿Por qué?** Tu router por defecto bloquea todas las conexiones entrantes desde Internet. Necesitas decirle: *"Cuando alguien llegue al puerto 7771, redirígelo a mi PC"*.

#### 2.1 Averiguar tu IP local

En la PC servidor, abre PowerShell y ejecuta:

```powershell
ipconfig
```

Busca la sección de tu adaptador activo (Wi-Fi o Ethernet) y anota la línea:

```
Dirección IPv4. . . . . . . . . . . . . . : 192.168.1.50
```

Esa es tu **IP local** (anótala, la necesitas en un momento).

> 💡 **Recomendación**: Asigna una IP local **fija** a tu PC servidor desde el router (sección "DHCP Reservation" o "Static Lease") para que no cambie.

#### 2.2 Entrar al panel del router

Abre el navegador y escribe una de estas direcciones (según la marca de tu router):

| Marca | URL típica |
|---|---|
| TP-Link | `http://192.168.0.1` o `http://tplinkwifi.net` |
| D-Link | `http://192.168.0.1` |
| Netgear | `http://routerlogin.net` o `http://192.168.1.1` |
| ASUS | `http://router.asus.com` o `http://192.168.1.1` |
| Huawei | `http://192.168.100.1` |
| Claro / Altice | `http://192.168.0.1` o `http://192.168.100.1` |
| Movistar | `http://192.168.1.1` |

Credenciales por defecto (si nunca las cambiaste):

| Usuario | Contraseña |
|---|---|
| `admin` | `admin` |
| `admin` | `password` |
| `admin` | *(vacío)* |

> Si no sabes las credenciales, busca la marca del router y busca en Google: *"usuario contraseña router [marca] [modelo]"*.

#### 2.3 Encontrar la sección de Port Forwarding

Los nombres varían según el router:

- **TP-Link**: `Forwarding` → `Virtual Servers`
- **D-Link**: `Advanced` → `Port Forwarding`
- **Netgear**: `Advanced` → `Advanced Setup` → `Port Forwarding/Port Triggering`
- **ASUS**: `WAN` → `Virtual Server / Port Forwarding`
- **Huawei**: `Forward Rules` → `Port Mapping`
- **Claro / Altice**: `NAT` → `Port Forwarding` o `Virtual Server`

#### 2.4 Crear la regla

Rellena los campos así:

| Campo | Valor |
|---|---|
| **Nombre / Description** | `Callidus` |
| **Service Type** | `TCP` (o `TCP/UDP`) |
| **External Port / Puerto externo** | `7771` |
| **Internal Port / Puerto interno** | `7771` |
| **Internal IP / IP local** | `192.168.1.50` (la de tu PC) |
| **Protocolo** | `TCP` |
| **Enable / Habilitar** | ✅ Sí |

> 💡 Si el router pide un **rango**, pon `7771` a `7771` (mismo puerto).

Guarda los cambios. Algunos routers requieren **reiniciar** para aplicar.

#### 2.5 Abrir el puerto en el firewall de Windows

Además del router, el firewall de Windows puede bloquear el puerto. Ejecuta **PowerShell como administrador**:

```powershell
New-NetFirewallRule `
  -DisplayName "Callidus 7771" `
  -Direction Inbound `
  -Protocol TCP `
  -LocalPort 7771 `
  -Action Allow `
  -Profile Any
```

Para eliminarla después:

```powershell
Remove-NetFirewallRule -DisplayName "Callidus 7771"
```

#### 2.6 Verificar que el puerto está abierto

Desde **otra red** (por ejemplo, tu celular con datos móviles):

```bash
ping callidus.servehttp.com
```

O mejor, desde una terminal en otra PC:

```powershell
Test-NetConnection -ComputerName callidus.servehttp.com -Port 7771
```

Resultado esperado:

```
TcpTestSucceeded : True
```

También puedes probar online: [https://www.yougetsignal.com/tools/open-ports/](https://www.yougetsignal.com/tools/open-ports/)

- **Remote Address**: `callidus.servehttp.com`
- **Port Number**: `7771`

Si dice **"Port is open"** → ¡Funciona! ✅

### 🧩 Paso 3 — Conectar desde el cliente remoto

En la otra PC, abre `client.py` y rellena:

| Campo | Valor |
|---|---|
| **Host** | `callidus.servehttp.com` |
| **Puerto** | `7771` |
| **Contraseña** | la que hayas configurado |

Pulsa **Conectar**. Deberías ver los archivos de tu PC servidor como si estuvieras sentado frente a ella. 🎉

### 🛡️ Alternativa SEGURA: Túnel SSH

**Recomendado** en lugar de exponer el puerto directamente. En lugar del paso 2, puedes usar SSH:

```bash
# En la PC cliente (la que se conecta)
ssh -L 7771:localhost:7771 usuario@callidus.servehttp.com
```

Luego en `client.py` usa host `127.0.0.1`. Todo el tráfico viaja **cifrado** por el túnel SSH. Necesitas un servidor SSH (OpenSSH) corriendo en la máquina servidor.

- **Windows**: Instalar **OpenSSH Server** desde *Configuración → Aplicaciones → Características opcionales*.
- **Linux/macOS**: Ya viene con `sshd` (activar con `sudo systemctl enable --now sshd`).

---

## 🖥️ Ejecución automática al iniciar Windows

Puedes hacer que el servidor Callidus **arranque solo** cuando enciendas la PC, sin necesidad de abrir una terminal manualmente.

### 📦 Opción A — Carpeta de Inicio (más simple)

**1. Crear el archivo `iniciar_callidus.bat`** en la carpeta del proyecto:

```batch
@echo off
title Callidus Server - by LuisMiguelsantoslm
cd /d "%~dp0"
echo.
echo ============================================================
echo   Callidus - Servidor de Archivos Remoto
echo   by Luis Miguel Santos (LuisMiguelsantoslm)
echo   Protocolo: CFS1
echo ============================================================
echo.
python server.py --yes
pause
```

> El flag `--yes` evita la pregunta de confirmación al compartir la raíz.

**2. Presionar `Win + R`** y escribir:

```
shell:startup
```

**3. Copiar** el archivo `iniciar_callidus.bat` **en esa carpeta**.

**4. Reiniciar** la PC para verificar. El servidor arrancará automáticamente.

**Para quitarlo**: borra el `.bat` de la carpeta Startup.

### 📦 Opción B — Programador de tareas (más robusto)

**1. Abrir** *Programador de tareas* (Task Scheduler) → **Crear tarea...**

**2. Pestaña "General":**

| Campo | Valor |
|---|---|
| Nombre | `Callidus Server` |
| Ejecutar con los privilegios más altos | ✅ Marcar |
| Configurar para | `Windows 10` (o tu versión) |

**3. Pestaña "Desencadenadores"** → **Nuevo...**

| Campo | Valor |
|---|---|
| Iniciar la tarea | `Al iniciar el equipo` |
| Retrasar tarea durante | `30 segundos` (opcional) |
| Habilitado | ✅ |

**4. Pestaña "Acciones"** → **Nuevo...**

| Campo | Valor |
|---|---|
| Acción | `Iniciar un programa` |
| Programa/script | `C:\Python314\python.exe` (ruta completa) |
| Argumentos | `server.py --yes` |
| Iniciar en | `C:\Users\L.M\Documents\Callidus` (carpeta del script) |

**5. Pestaña "Condiciones":**

- ❌ **Desmarcar** *"Iniciar la tarea solo si el equipo está conectado a la red eléctrica"* (para laptops).

**6. Pestaña "Configuración":**

- ✅ *"Si la tarea ya está en ejecución, aplicar la siguiente regla"* → `No iniciar una nueva instancia`.
- ✅ *"Detener la tarea si se ejecuta durante más de..."* → **DESMARCAR**.

**7. Guardar** y probar:

```powershell
# Ejecutar manualmente para verificar
schtasks /run /tn "Callidus Server"
```

**Para eliminar la tarea:**

```powershell
schtasks /delete /tn "Callidus Server" /f
```

### 📦 Opción C — Servicio de Windows (nivel avanzado)

Convierte el servidor en un **servicio de Windows** que corre en segundo plano sin sesión de usuario.

**1. Instalar `nssm`** (Non-Sucking Service Manager):

- Descarga: [https://nssm.cc/download](https://nssm.cc/download)
- Descomprime y copia `nssm.exe` a `C:\Windows\System32`.

**2. Instalar el servicio** (PowerShell como admin):

```powershell
nssm install CallidusServer "C:\Python314\python.exe" "C:\Users\L.M\Documents\Callidus\server.py --yes"
nssm set CallidusServer AppDirectory "C:\Users\L.M\Documents\Callidus"
nssm set CallidusServer Description "Servidor de archivos Callidus - by LuisMiguelsantoslm"
nssm set CallidusServer Start SERVICE_AUTO_START
nssm set CallidusServer AppStdout "C:\Users\L.M\Documents\Callidus\server.log"
nssm set CallidusServer AppStderr "C:\Users\L.M\Documents\Callidus\server.err.log"
```

**3. Iniciar el servicio:**

```powershell
nssm start CallidusServer
```

**4. Verificar:**

```powershell
nssm status CallidusServer     # debe decir SERVICE_RUNNING
```

**Comandos útiles:**

```powershell
nssm stop CallidusServer              # detener
nssm restart CallidusServer           # reiniciar
nssm remove CallidusServer confirm    # desinstalar
```

---

## ⌨️ Atajos de teclado

| Atajo | Acción |
|---|---|
| `F5` | Conectar al servidor |
| `F6` | Refrescar listado |
| `F2` | Renombrar seleccionado |
| `Ctrl + U` | Subir archivo(s) |
| `Ctrl + N` | Nueva carpeta |
| `Ctrl + F` | Enfocar búsqueda |
| `Alt + ←` | Atrás |
| `Alt + →` | Adelante |
| `Alt + ↑` | Subir un nivel |
| `Backspace` | Subir un nivel |
| `Enter` | Abrir carpeta seleccionada |
| `Suprimir` | Eliminar seleccionados |
| `Esc` | Cancelar transferencia |

---

## ⚙️ Configuración avanzada

### Argumentos del servidor

```bash
python server.py --help
```

| Argumento | Descripción | Default |
|---|---|---|
| `--host` | IP donde escuchar | `0.0.0.0` |
| `--port` | Puerto TCP | `7771` |
| `--shared` | Carpeta a compartir | Raíz de la unidad del script |
| `--yes` | Saltar la confirmación de raíz | `False` |

**Ejemplos:**

```bash
# Compartir una carpeta específica
python server.py --shared "C:\Users\L.M\Documents"

# Compartir otra unidad
python server.py --shared D:\

# Otro puerto
python server.py --port 9000

# Sin preguntar
python server.py --yes
```

### Ajustes del cliente

El cliente guarda automáticamente host, puerto y tamaño de ventana en:

```
C:\Users\TuUsuario\.callidus_client.json
```

Bórralo si quieres resetear la configuración.

### Parámetros del protocolo

En `server.py` puedes ajustar:

| Constante | Descripción | Default |
|---|---|---|
| `CHUNK_SIZE` | Tamaño de cada bloque de transferencia | `256 KB` |
| `COMPRESS_THRESHOLD` | Tamaño mínimo para comprimir mensajes | `256 bytes` |
| `HEARTBEAT_TIMEOUT` | Segundos sin ping antes de cerrar | `90` |
| `MAX_FAILED_ATTEMPTS` | Intentos fallidos antes de bloquear IP | `5` |
| `BLOCK_TIME` | Segundos de bloqueo tras superar intentos | `300` |

---

## 🔐 Seguridad

### ✅ Lo que está protegido

- Contraseña **nunca viaja en claro** (SHA-256 en el handshake).
- **Token de sesión** requerido en cada comando tras el login.
- **Path traversal** bloqueado (`../`, rutas absolutas, cambios de unidad).
- **Anti brute-force** por IP (5 intentos → 5 min bloqueado).
- **Filtro de archivos de sistema** en la raíz.
- **Confirmación interactiva** antes de compartir una unidad completa.

### ❌ Lo que NO está protegido

- **El canal no tiene TLS** → el tráfico viaja en texto plano.
- **No hay control de usuarios** — una sola contraseña, todos los permisos.
- **No hay logs persistentes** — los eventos se muestran solo en consola.

### 🛡️ Recomendaciones

1. **Cambia `admin123`** por una contraseña fuerte antes de usar.
2. **Usa un túnel SSH** en lugar de exponer el puerto (ver sección [No-IP](#-acceso-desde-internet-no-ip--port-forwarding)).
3. **Nunca compartas `C:\` entero** con datos sensibles.
4. Ejecuta el servidor con **cuenta de usuario limitada** (no admin).
5. **Cierra el puerto** en el router cuando no lo uses.
6. Revisa los logs del servidor regularmente por conexiones sospechosas.

---

## 🏗️ Arquitectura del protocolo CFS1

**CFS1** = *Callidus File Server v1*

El protocolo CFS1 es un protocolo binario propio diseñado específicamente para este proyecto. Combina lo mejor de varios enfoques:

- **Framing estilo Redis / Minecraft**: cabecera fija de 10 bytes con magic + versión + flags + longitud.
- **Compresión transparente**: zlib automático en mensajes de control mayores a 256 bytes.
- **Serialización**: `pickle` para mensajes estructurados, bytes crudos para chunks de archivo.
- **Autenticación**: SHA-256 + token de sesión (`secrets.token_hex`).

### Formato de frame

```
┌──────────┬─────────┬──────────┬──────────────┬─────────────────┐
│  MAGIC   │ VERSION │  FLAGS   │    LENGTH    │     PAYLOAD     │
│  4 bytes │ 1 byte  │  1 byte  │   4 bytes    │    N bytes      │
│ "CFS1"   │  0x02   │ 0x01=zlib│  big endian  │  (pickle+zlib)  │
└──────────┴─────────┴──────────┴──────────────┴─────────────────┘
```

### Flujo de conexión

```
CLIENTE                                    SERVIDOR
   │                                           │
   ├────── hello (version) ───────────────────►│
   │◄───── ok (server, version) ───────────────┤
   │                                           │
   ├────── auth (password) ───────────────────►│
   │                    [SHA-256 + anti-brute] │
   │◄───── ok (token, root_name) ──────────────┤
   │                                           │
   ├────── list (token, path) ────────────────►│
   │◄───── ok (items, path) ───────────────────┤
   │                                           │
   ├────── download_folder (token, path) ─────►│
   │◄───── manifest (total_files, total_size) ─┤
   │◄───── file_start (rel, size) ─────────────┤
   │◄───── [chunk] [chunk] [chunk] ... ────────┤
   │◄───── done ───────────────────────────────┤
   │                                           │
   ├────── bye ───────────────────────────────►│
```

### Comandos soportados

| Comando | Descripción |
|---|---|
| `hello` | Handshake inicial |
| `auth` | Autenticación con contraseña |
| `ping` | Heartbeat |
| `list` | Listar carpeta |
| `quick` | Obtener accesos rápidos |
| `stats` | Estadísticas del servidor |
| `mkdir` | Crear carpeta |
| `rename` | Renombrar |
| `delete` | Eliminar |
| `download` | Descargar un archivo |
| `download_folder` | Descargar carpeta recursivamente |
| `upload` | Subir un archivo |
| `bye` | Cerrar sesión |

---

## 📁 Estructura del proyecto

```
Callidus/
├── server.py               # Servidor Callidus (~500 líneas)
├── client.py               # Cliente GUI Callidus (~900 líneas)
├── README.md               # Este archivo
├── LICENSE                 # MIT — © Luis Miguel Santos
├── .gitignore              # Excluye __pycache__, *.pyc, etc.
├── requirements.txt        # Comentado: sin dependencias externas
├── iniciar_callidus.bat    # (opcional) arranque automático en Windows
└── docs/
    ├── PROTOCOLO.md        # Documentación técnica del protocolo CFS1
    └── CAPTURAS/           # Imágenes del cliente
```

> **Proyecto:** Callidus — **Autor:** Luis Miguel Santos — [@LuisMiguelsantoslm](https://github.com/LuisMiguelsantoslm)

---

## 🛠️ Roadmap

### ✅ Completado
- [x] Protocolo binario con framing + compresión
- [x] Autenticación SHA-256 + token de sesión
- [x] Navegación con historial (back/forward/up)
- [x] Breadcrumb clickable
- [x] Sidebar con accesos rápidos
- [x] Búsqueda en vivo
- [x] Ordenamiento por columnas
- [x] Descarga recursiva de carpetas
- [x] Cancelación de transferencias
- [x] Estadísticas del servidor
- [x] Arranque automático en Windows

### 🚧 En desarrollo
- [ ] Subida recursiva de carpetas (drag & drop)
- [ ] Preview de imágenes / texto
- [ ] Descarga en ZIP comprimido
- [ ] TLS con `ssl` nativo

### 💡 Ideas futuras
- [ ] Múltiples usuarios con permisos
- [ ] Modo servicio nativo (systemd en Linux)
- [ ] Cliente web (Flask + HTML)
- [ ] Sincronización bidireccional
- [ ] Compartir enlaces temporales

---

## 🤝 Contribuir

1. Haz un **fork** del proyecto.
2. Crea una rama para tu feature:
   ```bash
   git checkout -b feature/nueva-funcionalidad
   ```
3. Commitea tus cambios:
   ```bash
   git commit -am 'Añadir nueva funcionalidad'
   ```
4. Sube la rama:
   ```bash
   git push origin feature/nueva-funcionalidad
   ```
5. Abre un **Pull Request**.

### Estilo de código

- PEP 8 (líneas ≤ 100 caracteres).
- Docstrings en funciones públicas.
- Sin dependencias externas sin justificación clara.

---

## 📜 Licencia

Este proyecto está licenciado bajo la **MIT License** — ver el archivo [LICENSE](LICENSE) para más detalles.

```
MIT License

Copyright (c) 2025 Luis Miguel Santos (LuisMiguelsantoslm)

Project: Callidus — Remote File Server & Client
Protocol: CFS1 (Callidus File Server v1)

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

---

## 📞 Contacto

<table>
  <tr>
    <td><strong>Autor</strong></td>
    <td>Luis Miguel Santos</td>
  </tr>
  <tr>
    <td><strong>Usuario GitHub</strong></td>
    <td><a href="https://github.com/LuisMiguelsantoslm">@LuisMiguelsantoslm</a></td>
  </tr>
  <tr>
    <td><strong>Repositorio</strong></td>
    <td><a href="https://github.com/LuisMiguelsantoslm/Callidus">github.com/LuisMiguelsantoslm/Callidus</a></td>
  </tr>
  <tr>
    <td><strong>Issues</strong></td>
    <td><a href="https://github.com/LuisMiguelsantoslm/Callidus/issues">Reportar un problema</a></td>
  </tr>
  <tr>
    <td><strong>Discusiones</strong></td>
    <td><a href="https://github.com/LuisMiguelsantoslm/Callidus/discussions">Ideas y preguntas</a></td>
  </tr>
</table>

---

## 🌟 Créditos

- **Autor original, desarrollador principal y creador del protocolo CFS1**: **Luis Miguel Santos** (`LuisMiguelsantoslm`)
- **Diseño de la arquitectura cliente-servidor**: Luis Miguel Santos
- **Cliente GUI Tkinter**: Luis Miguel Santos
- **Documentación**: Luis Miguel Santos
- **Inspiración**: VS Code, Redis, Minecraft, explorador de Windows

---

<p align="center">
  <strong>⭐ Si este proyecto te fue útil, dale una estrella en GitHub ⭐</strong>
  <br><br>
  <strong>Callidus</strong> — Hecho con ❤️ por <a href="https://github.com/LuisMiguelsantoslm"><strong>Luis Miguel Santos</strong></a>
  <br>
  <em>Proyecto educativo de código abierto · 2025</em>
</p>

