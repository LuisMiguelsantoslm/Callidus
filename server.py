#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CFS1 Pro - Servidor de archivos.

Comparte por defecto LA RAIZ de la unidad donde esta el script.
Ejemplos:
    python server.py                       -> C:\\ (o la unidad del script)
    python server.py --shared D:\\
    python server.py --shared "C:\\Users\\L.M\\Documents"
    python server.py --port 7771 --yes     (no pedir confirmacion)
"""
import argparse
import datetime
import hashlib
import os
import pickle
import secrets
import shutil
import socket
import struct
import string
import sys
import threading
import time
import zlib
from pathlib import Path

# ==================== PROTOCOLO ====================
MAGIC = b'CFS1'
PROTO_VERSION = 2
HEADER_FMT = '!4sBBI'
HEADER_SIZE = struct.calcsize(HEADER_FMT)
FLAG_COMPRESSED = 0x01

# ==================== CONFIG ====================
DEFAULT_HOST = '0.0.0.0'
DEFAULT_PORT = 7771
PASSWORD_HASH = hashlib.sha256('admin123'.encode()).hexdigest()
CHUNK_SIZE = 256 * 1024
COMPRESS_THRESHOLD = 256
MAX_FAILED_ATTEMPTS = 5
BLOCK_TIME = 300

# ==================== ESTADO GLOBAL ====================
SHARED_DIR: Path = None
_lock = threading.Lock()
_failed_attempts = {}
_server_start = time.time()
_active_clients = set()
_stats_cache = {'data': None, 'ts': 0}


# ==================== LOG ====================
def log(tag, *args):
    ts = datetime.datetime.now().strftime('%H:%M:%S')
    print(f'[{ts}] [{tag}]', *args, flush=True)


# ==================== FRAMING ====================
def recv_exact(sock, n):
    buf = b''
    while len(buf) < n:
        chunk = sock.recv(n - len(buf))
        if not chunk:
            return None
        buf += chunk
    return buf


def send_frame(sock, data):
    header = struct.pack(HEADER_FMT, MAGIC, PROTO_VERSION, 0, len(data))
    sock.sendall(header + data)


def recv_frame(sock):
    header = recv_exact(sock, HEADER_SIZE)
    if header is None:
        return None
    magic, ver, flags, length = struct.unpack(HEADER_FMT, header)
    if magic != MAGIC:
        raise ValueError('Magic incorrecto')
    payload = recv_exact(sock, length) if length else b''
    if payload is None:
        return None
    if flags & FLAG_COMPRESSED:
        payload = zlib.decompress(payload)
    return payload


def send_msg(sock, obj):
    data = pickle.dumps(obj)
    if len(data) > COMPRESS_THRESHOLD:
        comp = zlib.compress(data, 6)
        if len(comp) < len(data):
            header = struct.pack(HEADER_FMT, MAGIC, PROTO_VERSION, FLAG_COMPRESSED, len(comp))
            sock.sendall(header + comp)
            return
    header = struct.pack(HEADER_FMT, MAGIC, PROTO_VERSION, 0, len(data))
    sock.sendall(header + data)


def recv_msg(sock):
    data = recv_frame(sock)
    return pickle.loads(data) if data else None


# ==================== UTILIDADES ====================
def safe_path(rel):
    rel = (rel or '').strip().lstrip('/\\').replace('\\', '/')
    if ':' in rel:
        raise ValueError('Ruta no permitida')
    target = (SHARED_DIR / rel).resolve()
    try:
        target.relative_to(SHARED_DIR.resolve())
    except ValueError:
        raise ValueError('Ruta fuera del directorio compartido')
    return target


def human_size(n):
    for unit in ('B', 'KB', 'MB', 'GB', 'TB'):
        if n < 1024:
            return f'{n:.1f} {unit}' if unit != 'B' else f'{n} B'
        n /= 1024
    return f'{n:.1f} PB'


def is_blocked(ip):
    if ip not in _failed_attempts:
        return False
    count, last = _failed_attempts[ip]
    if count >= MAX_FAILED_ATTEMPTS and (time.time() - last) < BLOCK_TIME:
        return True
    if (time.time() - last) >= BLOCK_TIME:
        del _failed_attempts[ip]
    return False


def register_fail(ip):
    count, _ = _failed_attempts.get(ip, (0, 0))
    _failed_attempts[ip] = (count + 1, time.time())


def clear_fails(ip):
    _failed_attempts.pop(ip, None)


def detect_script_root():
    return Path(Path(__file__).resolve().anchor)


def is_root_of_drive(path):
    p = Path(path).resolve()
    return p == Path(p.anchor)


# ==================== QUICK ACCESS ====================
def get_quick_access():
    """Devuelve lista de accesos rapidos que estan dentro de SHARED_DIR."""
    candidates = []
    home = Path.home()
    
    # Unidades (Windows)
    if os.name == 'nt':
        for letter in string.ascii_uppercase:
            p = Path(f'{letter}:\\')
            try:
                if p.exists():
                    candidates.append((f'💽  Unidad {letter}:', p))
            except Exception:
                pass
    
    # Carpetas de usuario
    user_dirs = [
        ('🏠  Inicio', home),
        ('🖥️  Escritorio', home / 'Desktop'),
        ('🖥️  Escritorio', home / 'OneDrive' / 'Desktop'),
        ('📄  Documentos', home / 'Documents'),
        ('📄  Documentos', home / 'OneDrive' / 'Documents'),
        ('🖼️  Imágenes', home / 'Pictures'),
        ('🖼️  Imágenes', home / 'OneDrive' / 'Pictures'),
        ('🎵  Música', home / 'Music'),
        ('🎵  Música', home / 'OneDrive' / 'Music'),
        ('🎬  Vídeos', home / 'Videos'),
        ('🎬  Vídeos', home / 'OneDrive' / 'Videos'),
        ('⬇️  Descargas', home / 'Downloads'),
    ]
    
    seen_labels = set()
    result = []
    
    for label, p in user_dirs:
        if label in seen_labels:
            continue
        try:
            if not p.is_dir():
                continue
            rel = p.resolve().relative_to(SHARED_DIR.resolve()).as_posix()
            result.append({'label': label, 'path': rel, 'kind': 'user'})
            seen_labels.add(label)
        except (ValueError, OSError):
            continue
    
    # Unidades primero
    drives = []
    for label, p in candidates:
        try:
            if not p.exists():
                continue
            rel = p.resolve().relative_to(SHARED_DIR.resolve()).as_posix()
            drives.append({'label': label, 'path': rel if rel != '.' else '', 'kind': 'drive'})
        except (ValueError, OSError):
            # La unidad no esta dentro de SHARED_DIR (compartimos otra)
            continue
    
    return {'drives': drives, 'user': result}


# ==================== OPERACIONES ====================
def op_list(req, session):
    rel = req.get('path', '')
    folder = safe_path(rel)
    if not folder.is_dir():
        return {'status': 'error', 'msg': 'No es una carpeta'}

    items = []
    with _lock:
        try:
            entries = list(folder.iterdir())
        except PermissionError:
            return {'status': 'error', 'msg': 'Acceso denegado'}
        except OSError as ex:
            return {'status': 'error', 'msg': f'Error: {ex}'}

        # Ocultar basura de Windows cuando estamos en raiz
        hidden = {'System Volume Information', '$RECYCLE.BIN', 'Recovery',
                  'PerfLogs', 'Config.Msi', '$WinREAgent'}
        is_root = (folder.resolve() == SHARED_DIR.resolve())

        for entry in entries:
            try:
                if is_root and entry.name in hidden:
                    continue
                st = entry.stat()
                items.append({
                    'name': entry.name,
                    'is_dir': entry.is_dir(),
                    'size': 0 if entry.is_dir() else st.st_size,
                    'mtime': int(st.st_mtime),
                })
            except (OSError, PermissionError):
                pass

    return {'status': 'ok', 'items': items, 'path': rel}


def op_mkdir(req, session):
    target = safe_path(req['path'])
    with _lock:
        target.mkdir(parents=True, exist_ok=False)
    return {'status': 'ok'}


def op_rename(req, session):
    src = safe_path(req['old'])
    dst = safe_path(req['new'])
    if not src.exists():
        return {'status': 'error', 'msg': 'No existe'}
    if dst.exists():
        return {'status': 'error', 'msg': 'El destino ya existe'}
    with _lock:
        src.rename(dst)
    return {'status': 'ok'}


def op_delete(req, session):
    target = safe_path(req['path'])
    if not target.exists():
        return {'status': 'error', 'msg': 'No existe'}
    if target.resolve() == SHARED_DIR.resolve():
        return {'status': 'error', 'msg': 'No se puede borrar la raiz'}
    with _lock:
        if target.is_dir():
            shutil.rmtree(target)
        else:
            target.unlink()
    return {'status': 'ok'}


def op_quick(req, session):
    return {'status': 'ok', **get_quick_access()}


def op_stats(req, session):
    # Cache de 30 segundos
    now = time.time()
    if _stats_cache['data'] and (now - _stats_cache['ts']) < 30:
        return {'status': 'ok', **_stats_cache['data']}

    files = 0
    total = 0
    t0 = time.time()
    deadline = t0 + 4.0  # limite 4 segundos

    for root, dirs, filenames in os.walk(SHARED_DIR):
        if time.time() > deadline:
            break
        for f in filenames:
            files += 1
            try:
                total += os.path.getsize(os.path.join(root, f))
            except OSError:
                pass
        if files > 200000:
            break

    data = {
        'uptime': int(time.time() - _server_start),
        'files': files,
        'bytes': total,
        'clients': len(_active_clients),
        'path': str(SHARED_DIR),
    }
    _stats_cache['data'] = data
    _stats_cache['ts'] = now
    return {'status': 'ok', **data}


# ==================== TRANSFERENCIAS ====================
def op_download(sock, req, session):
    target = safe_path(req['path'])
    if not target.is_file():
        send_msg(sock, {'status': 'error', 'msg': 'Archivo no encontrado'})
        return
    try:
        size = target.stat().st_size
    except OSError as ex:
        send_msg(sock, {'status': 'error', 'msg': str(ex)})
        return

    send_msg(sock, {'status': 'ok', 'size': size, 'name': target.name})

    sent = 0
    t0 = time.time()
    try:
        with open(target, 'rb') as f:
            while sent < size:
                chunk = f.read(CHUNK_SIZE)
                if not chunk:
                    break
                send_frame(sock, chunk)
                sent += len(chunk)
    except OSError as ex:
        log('ERR', f'DL {target}: {ex}')
        return
    dt = max(time.time() - t0, 0.001)
    log('DL', f'{target.name} → {human_size(size)} en {dt:.1f}s')
    session['bytes_out'] += size


def op_download_folder(sock, req, session):
    """Envia manifest + archivos uno por uno preservando estructura."""
    target = safe_path(req['path'])
    if not target.is_dir():
        send_msg(sock, {'status': 'error', 'msg': 'No es una carpeta'})
        return

    # Recolectar archivos
    files = []
    total_size = 0
    with _lock:
        for root, dirs, filenames in os.walk(target):
            for fn in filenames:
                full = Path(root) / fn
                try:
                    size = full.stat().st_size
                    rel = full.relative_to(target).as_posix()
                    files.append((rel, size, full))
                    total_size += size
                except OSError:
                    pass

    send_msg(sock, {
        'status': 'ok',
        'kind': 'manifest',
        'name': target.name,
        'total_files': len(files),
        'total_size': total_size,
    })

    t0 = time.time()
    sent_total = 0
    for rel, size, full in files:
        send_msg(sock, {
            'status': 'ok',
            'kind': 'file_start',
            'rel': rel,
            'size': size,
        })
        try:
            with open(full, 'rb') as f:
                sent = 0
                while sent < size:
                    chunk = f.read(CHUNK_SIZE)
                    if not chunk:
                        break
                    send_frame(sock, chunk)
                    sent += len(chunk)
            sent_total += size
        except OSError as ex:
            log('ERR', f'DL folder {full}: {ex}')
            # enviar frame vacio para que el cliente no se quede colgado
            send_frame(sock, b'')
            # continuar con el siguiente

    send_msg(sock, {'status': 'ok', 'kind': 'done'})
    dt = max(time.time() - t0, 0.001)
    log('DL', f'[folder] {target.name} → {len(files)} archivos, '
              f'{human_size(sent_total)} en {dt:.1f}s')
    session['bytes_out'] += sent_total


def op_upload(sock, req, session):
    target = safe_path(req['path'])
    size = req['size']
    try:
        target.parent.mkdir(parents=True, exist_ok=True)
    except OSError as ex:
        send_msg(sock, {'status': 'error', 'msg': str(ex)})
        return
    send_msg(sock, {'status': 'ok'})

    received = 0
    t0 = time.time()
    try:
        with open(target, 'wb') as f:
            while received < size:
                chunk = recv_frame(sock)
                if chunk is None:
                    break
                f.write(chunk)
                received += len(chunk)
    except OSError as ex:
        log('ERR', f'UL {target}: {ex}')
        return

    send_msg(sock, {'status': 'ok'})
    dt = max(time.time() - t0, 0.001)
    log('UL', f'{target.name} ← {human_size(size)} en {dt:.1f}s')
    session['bytes_in'] += size


# ==================== HANDLER DE CLIENTE ====================
def handle_client(conn, addr):
    ip = addr[0]
    session = {
        'ip': ip, 'port': addr[1], 'token': None,
        'started': time.time(), 'bytes_in': 0, 'bytes_out': 0,
    }

    if is_blocked(ip):
        log('BLOCK', f'{ip} bloqueado')
        try:
            send_msg(conn, {'status': 'error', 'msg': 'IP bloqueada'})
        except Exception:
            pass
        conn.close()
        return

    _active_clients.add(ip)
    log('CONN', f'{ip}:{addr[1]}')

    try:
        hello = recv_msg(conn)
        if not hello or hello.get('cmd') != 'hello':
            return
        send_msg(conn, {'status': 'ok', 'server': 'CFS1 Pro',
                        'version': PROTO_VERSION})

        auth = recv_msg(conn)
        if not auth or auth.get('cmd') != 'auth':
            return
        given = hashlib.sha256(auth.get('password', '').encode()).hexdigest()
        if given != PASSWORD_HASH:
            register_fail(ip)
            log('AUTH', f'{ip} → FALLO')
            send_msg(conn, {'status': 'error', 'msg': 'Contraseña incorrecta'})
            return

        clear_fails(ip)
        token = secrets.token_hex(32)
        session['token'] = token
        send_msg(conn, {'status': 'ok', 'token': token,
                        'root_name': SHARED_DIR.name or str(SHARED_DIR)})
        log('AUTH', f'{ip} → OK')

        while True:
            data = recv_frame(conn)
            if data is None:
                break
            try:
                req = pickle.loads(data)
            except Exception:
                continue
            cmd = req.get('cmd')
            if cmd == 'ping':
                send_msg(conn, {'status': 'ok', 'type': 'pong'})
                continue
            if cmd == 'bye':
                break
            if req.get('token') != session['token']:
                send_msg(conn, {'status': 'error', 'msg': 'Token inválido'})
                continue
            try:
                if cmd == 'list':
                    send_msg(conn, op_list(req, session))
                elif cmd == 'quick':
                    send_msg(conn, op_quick(req, session))
                elif cmd == 'stats':
                    send_msg(conn, op_stats(req, session))
                elif cmd == 'mkdir':
                    send_msg(conn, op_mkdir(req, session))
                elif cmd == 'rename':
                    send_msg(conn, op_rename(req, session))
                elif cmd == 'delete':
                    send_msg(conn, op_delete(req, session))
                elif cmd == 'download':
                    op_download(conn, req, session)
                elif cmd == 'download_folder':
                    op_download_folder(conn, req, session)
                elif cmd == 'upload':
                    op_upload(conn, req, session)
                else:
                    send_msg(conn, {'status': 'error', 'msg': f'Cmd desconocido: {cmd}'})
            except ValueError as ex:
                send_msg(conn, {'status': 'error', 'msg': str(ex)})
            except Exception as ex:
                log('ERR', f'{cmd}: {type(ex).__name__}: {ex}')
                try:
                    send_msg(conn, {'status': 'error', 'msg': str(ex)})
                except Exception:
                    pass
    except Exception as ex:
        log('ERR', f'{ip}: {type(ex).__name__}: {ex}')
    finally:
        _active_clients.discard(ip)
        try:
            conn.close()
        except Exception:
            pass
        uptime = time.time() - session['started']
        log('BYE', f'{ip}:{addr[1]} tras {uptime:.0f}s '
                  f'(in={human_size(session["bytes_in"])}, '
                  f'out={human_size(session["bytes_out"])})')


# ==================== MAIN ====================
def main():
    global SHARED_DIR
    ap = argparse.ArgumentParser(description='CFS1 Pro Server')
    ap.add_argument('--host', default=DEFAULT_HOST)
    ap.add_argument('--port', type=int, default=DEFAULT_PORT)
    ap.add_argument('--shared', default=None)
    ap.add_argument('--yes', action='store_true')
    args = ap.parse_args()

    if args.shared:
        SHARED_DIR = Path(args.shared).expanduser().resolve()
    else:
        SHARED_DIR = detect_script_root()

    if not SHARED_DIR.is_dir():
        print(f'ERROR: "{SHARED_DIR}" no es una carpeta válida')
        sys.exit(1)

    if is_root_of_drive(SHARED_DIR) and not args.yes:
        print()
        print('=' * 68)
        print('  ⚠️  AVISO DE SEGURIDAD')
        print('=' * 68)
        print(f'  Compartiendo TODA la unidad:  {SHARED_DIR}')
        print()
        print('  Cualquiera con la contraseña podrá leer, escribir y BORRAR')
        print('  cualquier archivo de esta unidad.')
        print()
        print('  Recomendaciones:')
        print('    - Cambia la contraseña en server.py')
        print('    - NO expongas el puerto a Internet sin túnel SSH/VPN')
        print('=' * 68)
        try:
            ans = input('  Escribe "si" para continuar: ').strip().lower()
        except (EOFError, KeyboardInterrupt):
            ans = ''
        if ans not in ('si', 'sí', 's', 'yes', 'y'):
            print('Cancelado.')
            sys.exit(0)
        print()

    srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    srv.bind((args.host, args.port))
    srv.listen(50)

    log('SRV', f'CFS1 Pro v{PROTO_VERSION} en {args.host}:{args.port}')
    log('SRV', f'Compartiendo: {SHARED_DIR}')
    log('SRV', 'Ctrl+C para detener')

    try:
        while True:
            conn, addr = srv.accept()
            threading.Thread(target=handle_client,
                             args=(conn, addr), daemon=True).start()
    except KeyboardInterrupt:
        log('SRV', 'Cerrando...')
    finally:
        srv.close()


if __name__ == '__main__':
    main()