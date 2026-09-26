#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CFS1 Pro - Cliente de archivos (Tkinter).
"""
import json
import os
import pickle
import queue
import socket
import struct
import threading
import time
import tkinter as tk
import traceback
import zlib
from pathlib import Path
from tkinter import ttk, filedialog, messagebox, simpledialog

MAGIC = b'CFS1'
PROTO_VERSION = 2
HEADER_FMT = '!4sBBI'
HEADER_SIZE = struct.calcsize(HEADER_FMT)
FLAG_COMPRESSED = 0x01
CHUNK_SIZE = 256 * 1024
COMPRESS_THRESHOLD = 256

SETTINGS_FILE = Path.home() / '.cfs1_pro.json'
DEFAULT_HOST = 'callidus.servehttp.com'
DEFAULT_PORT = '7771'

# ==================== TEMA ====================
C = {
    'bg': '#1e1e1e',
    'bg_alt': '#252526',
    'bg_dark': '#181818',
    'bg_light': '#2d2d30',
    'fg': '#d4d4d4',
    'fg_dim': '#858585',
    'accent': '#007acc',
    'accent_h': '#1a8ad4',
    'success': '#4ec9b0',
    'error': '#f48771',
    'warn': '#dcdcaa',
    'border': '#3c3c3c',
    'select': '#094771',
    'row_alt': '#2a2a2b',
    'sidebar': '#252526',
    'sidebar_sel': '#37373d',
}


# ==================== UTILS ====================
def human_size(n):
    for unit in ('B', 'KB', 'MB', 'GB', 'TB'):
        if n < 1024:
            return f'{n:.1f} {unit}' if unit != 'B' else f'{n} B'
        n /= 1024
    return f'{n:.1f} PB'


def human_time(s):
    s = int(s)
    if s < 60: return f'{s}s'
    if s < 3600: return f'{s//60}m {s%60}s'
    return f'{s//3600}h {(s%3600)//60}m'


def fmt_date(ts):
    return time.strftime('%Y-%m-%d %H:%M', time.localtime(ts))


def file_icon(name, is_dir):
    if is_dir:
        return '📁'
    ext = os.path.splitext(name)[1].lower()
    if ext in ('.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp', '.svg', '.ico', '.tiff'):
        return '🖼️'
    if ext in ('.mp3', '.wav', '.flac', '.ogg', '.m4a', '.aac', '.wma'):
        return '🎵'
    if ext in ('.mp4', '.mkv', '.avi', '.mov', '.webm', '.flv', '.wmv', '.m4v'):
        return '🎬'
    if ext in ('.zip', '.rar', '.7z', '.tar', '.gz', '.bz2', '.xz'):
        return '📦'
    if ext == '.pdf': return '📕'
    if ext in ('.doc', '.docx', '.odt', '.rtf'): return '📘'
    if ext in ('.xls', '.xlsx', '.ods', '.csv'): return '📗'
    if ext in ('.ppt', '.pptx', '.odp'): return '📙'
    if ext in ('.py', '.js', '.ts', '.html', '.css', '.java', '.c', '.cpp',
               '.rs', '.go', '.rb', '.php', '.sh', '.ps1', '.bat', '.cmd'):
        return '📜'
    if ext in ('.exe', '.msi', '.com'): return '⚙️'
    if ext in ('.txt', '.md', '.log', '.json', '.xml', '.yml', '.yaml', '.ini', '.cfg', '.toml'):
        return '📄'
    if ext in ('.iso', '.img', '.dmg'): return '💿'
    if ext in ('.db', '.sqlite', '.sql'): return '🗄️'
    if ext in ('.ttf', '.otf', '.woff', '.woff2'): return '🔤'
    return '📄'


def load_settings():
    try:
        return json.loads(SETTINGS_FILE.read_text(encoding='utf-8'))
    except Exception:
        return {}


def save_settings(d):
    try:
        SETTINGS_FILE.write_text(json.dumps(d, indent=2), encoding='utf-8')
    except Exception:
        pass


def unique_path(path):
    if not os.path.exists(path):
        return path
    base, ext = os.path.splitext(path)
    i = 1
    while os.path.exists(f'{base} ({i}){ext}'):
        i += 1
    return f'{base} ({i}){ext}'


# ==================== CLIENTE ====================
class CFS1Client:
    def __init__(self, root):
        self.root = root
        self.root.title('CFS1 Pro · Explorador Remoto')
        self.root.geometry('1240x740')
        self.root.minsize(900, 560)
        self.root.configure(bg=C['bg'])

        # Estado
        self.sock = None
        self.connected = False
        self.token = None
        self.root_name = ''
        self.current_path = ''
        self.all_items = []
        self.quick_data = {'drives': [], 'user': []}
        self.history = []
        self.hist_idx = -1
        self.sort_col = 'name'
        self.sort_rev = False
        self.transfer_busy = False
        self.transfer_cancel = False
        self.io_lock = threading.Lock()
        self.msg_queue = queue.Queue()

        self._build_style()
        self._build_ui()
        self._restore_settings()

        self.root.after(60, self._process_queue)
        self.root.protocol('WM_DELETE_WINDOW', self.on_close)

    # ---------------- STYLE ----------------
    def _build_style(self):
        s = ttk.Style()
        try: s.theme_use('clam')
        except Exception: pass

        s.configure('.', background=C['bg'], foreground=C['fg'],
                    fieldbackground=C['bg_alt'], bordercolor=C['border'])
        s.configure('TFrame', background=C['bg'])
        s.configure('Side.TFrame', background=C['sidebar'])
        s.configure('TLabel', background=C['bg'], foreground=C['fg'])
        s.configure('Side.TLabel', background=C['sidebar'], foreground=C['fg_dim'])
        s.configure('Dim.TLabel', foreground=C['fg_dim'])
        s.configure('Title.TLabel', font=('Segoe UI', 10, 'bold'),
                    foreground=C['accent'], background=C['bg'])
        s.configure('TButton', background=C['bg_light'], foreground=C['fg'],
                    borderwidth=0, focusthickness=0, padding=(10, 6),
                    font=('Segoe UI', 9))
        s.map('TButton',
              background=[('active', C['accent']), ('pressed', C['accent_h']),
                          ('disabled', C['bg_dark'])],
              foreground=[('disabled', C['fg_dim'])])
        s.configure('Accent.TButton', background=C['accent'], foreground='white',
                    font=('Segoe UI', 9, 'bold'))
        s.map('Accent.TButton', background=[('active', C['accent_h'])])
        s.configure('Icon.TButton', padding=(8, 6), font=('Segoe UI', 11))
        s.configure('Side.TButton', background=C['sidebar'], foreground=C['fg'],
                    borderwidth=0, padding=(10, 6), anchor='w',
                    font=('Segoe UI', 9))
        s.map('Side.TButton',
              background=[('active', C['sidebar_sel'])],
              foreground=[('active', 'white')])
        s.configure('Crumb.TButton', background=C['bg_alt'], foreground=C['fg'],
                    borderwidth=0, padding=(8, 4), font=('Segoe UI', 9))
        s.map('Crumb.TButton',
              background=[('active', C['accent'])],
              foreground=[('active', 'white')])
        s.configure('TEntry', fieldbackground=C['bg_alt'], foreground=C['fg'],
                    insertcolor=C['fg'], bordercolor=C['border'],
                    lightcolor=C['border'], darkcolor=C['border'])
        s.configure('TLabelframe', background=C['bg'], foreground=C['accent'],
                    bordercolor=C['border'])
        s.configure('TLabelframe.Label', background=C['bg'], foreground=C['accent'],
                    font=('Segoe UI', 10, 'bold'))
        s.configure('Treeview', background=C['bg_alt'], foreground=C['fg'],
                    fieldbackground=C['bg_alt'], borderwidth=0, rowheight=28,
                    font=('Segoe UI', 10))
        s.configure('Treeview.Heading', background=C['bg_dark'], foreground=C['fg'],
                    relief='flat', font=('Segoe UI', 9, 'bold'), padding=(6, 6))
        s.map('Treeview.Heading', background=[('active', C['accent'])])
        s.map('Treeview', background=[('selected', C['select'])],
              foreground=[('selected', 'white')])
        s.configure('Vertical.TScrollbar', background=C['bg_alt'],
                    troughcolor=C['bg_dark'], bordercolor=C['bg_dark'],
                    arrowcolor=C['fg_dim'])
        s.configure('Horizontal.TProgressbar', background=C['accent'],
                    troughcolor=C['bg_dark'], bordercolor=C['bg_dark'],
                    lightcolor=C['accent'], darkcolor=C['accent'])
        s.configure('TSeparator', background=C['border'])

    # ---------------- UI ----------------
    def _build_ui(self):
        # ===== Top bar =====
        top = tk.Frame(self.root, bg=C['bg_dark'], height=46)
        top.pack(fill='x', side='top')
        top.pack_propagate(False)

        tk.Label(top, text='🗂️  CFS1 Pro', bg=C['bg_dark'], fg=C['accent'],
                 font=('Segoe UI', 13, 'bold')).pack(side='left', padx=15)

        self.conn_ind = tk.Label(top, text='● Desconectado', bg=C['bg_dark'],
                                  fg=C['error'], font=('Segoe UI', 9, 'bold'))
        self.conn_ind.pack(side='left', padx=10)

        self.stats_lbl = tk.Label(top, text='', bg=C['bg_dark'], fg=C['fg_dim'],
                                   font=('Segoe UI', 9))
        self.stats_lbl.pack(side='right', padx=15)

        # ===== Connection bar =====
        cb = ttk.Frame(self.root)
        cb.pack(fill='x', padx=12, pady=(8, 4))
        ttk.Label(cb, text='Host:').pack(side='left')
        self.host_var = tk.StringVar(value=DEFAULT_HOST)
        ttk.Entry(cb, textvariable=self.host_var, width=26).pack(side='left', padx=(4, 10))
        ttk.Label(cb, text='Puerto:').pack(side='left')
        self.port_var = tk.StringVar(value=DEFAULT_PORT)
        ttk.Entry(cb, textvariable=self.port_var, width=7).pack(side='left', padx=(4, 10))
        ttk.Label(cb, text='Contraseña:').pack(side='left')
        self.pass_var = tk.StringVar()
        pw = ttk.Entry(cb, textvariable=self.pass_var, show='●', width=18)
        pw.pack(side='left', padx=(4, 10))
        pw.bind('<Return>', lambda e: self.connect())
        self.btn_conn = ttk.Button(cb, text='Conectar', style='Accent.TButton',
                                    command=self.connect)
        self.btn_conn.pack(side='left', padx=3)
        self.btn_disc = ttk.Button(cb, text='Desconectar',
                                    command=self.disconnect, state='disabled')
        self.btn_disc.pack(side='left', padx=3)

        # ===== Toolbar =====
        tb = ttk.Frame(self.root)
        tb.pack(fill='x', padx=12, pady=2)

        self.btn_back = ttk.Button(tb, text='◀', width=3, style='Icon.TButton',
                                    command=self.go_back, state='disabled')
        self.btn_back.pack(side='left', padx=1)
        self.btn_fwd = ttk.Button(tb, text='▶', width=3, style='Icon.TButton',
                                   command=self.go_forward, state='disabled')
        self.btn_fwd.pack(side='left', padx=1)
        self.btn_up = ttk.Button(tb, text='▲', width=3, style='Icon.TButton',
                                  command=self.go_up, state='disabled')
        self.btn_up.pack(side='left', padx=1)
        self.btn_ref = ttk.Button(tb, text='⟳', width=3, style='Icon.TButton',
                                   command=self.refresh, state='disabled')
        self.btn_ref.pack(side='left', padx=1)

        ttk.Separator(tb, orient='vertical').pack(side='left', fill='y', padx=8)

        self.btn_dl = ttk.Button(tb, text='⬇  Descargar', command=self.download_selected,
                                  state='disabled')
        self.btn_dl.pack(side='left', padx=2)
        self.btn_ul = ttk.Button(tb, text='⬆  Subir', command=self.upload_file,
                                  state='disabled')
        self.btn_ul.pack(side='left', padx=2)
        self.btn_mk = ttk.Button(tb, text='📁  Nueva carpeta', command=self.mkdir,
                                  state='disabled')
        self.btn_mk.pack(side='left', padx=2)
        self.btn_rn = ttk.Button(tb, text='✎  Renombrar', command=self.rename_selected,
                                  state='disabled')
        self.btn_rn.pack(side='left', padx=2)
        self.btn_del = ttk.Button(tb, text='🗑  Eliminar', command=self.delete_selected,
                                   state='disabled')
        self.btn_del.pack(side='left', padx=2)

        ttk.Separator(tb, orient='vertical').pack(side='left', fill='y', padx=8)

        self.btn_stats = ttk.Button(tb, text='📊  Stats', command=self.show_stats,
                                     state='disabled')
        self.btn_stats.pack(side='left', padx=2)

        # Search
        sf = ttk.Frame(tb)
        sf.pack(side='right')
        ttk.Label(sf, text='🔍').pack(side='left')
        self.search_var = tk.StringVar()
        self.search_var.trace_add('write', lambda *a: self._apply_filter())
        ttk.Entry(sf, textvariable=self.search_var, width=28).pack(side='left', padx=4)

        # ===== Breadcrumb =====
        bc = ttk.Frame(self.root)
        bc.pack(fill='x', padx=12, pady=(6, 4))
        ttk.Label(bc, text='📂', style='Dim.TLabel').pack(side='left', padx=(0, 6))
        self.crumb_frame = ttk.Frame(bc)
        self.crumb_frame.pack(side='left', fill='x', expand=True)

        # ===== Main: sidebar + tree =====
        main = ttk.PanedWindow(self.root, orient='horizontal')
        main.pack(fill='both', expand=True, padx=12, pady=4)

        # Sidebar
        side_outer = tk.Frame(main, bg=C['sidebar'], width=220)
        side_outer.pack_propagate(False)
        main.add(side_outer, weight=0)

        side_hdr = tk.Frame(side_outer, bg=C['sidebar'])
        side_hdr.pack(fill='x', padx=10, pady=(10, 4))
        tk.Label(side_hdr, text='ACCESO RÁPIDO', bg=C['sidebar'],
                 fg=C['fg_dim'], font=('Segoe UI', 8, 'bold')).pack(anchor='w')

        # Scrollable sidebar
        canvas = tk.Canvas(side_outer, bg=C['sidebar'], highlightthickness=0, bd=0)
        self.side_inner = tk.Frame(canvas, bg=C['sidebar'])
        vsb = ttk.Scrollbar(side_outer, orient='vertical', command=canvas.yview)
        canvas.configure(yscrollcommand=vsb.set)
        vsb.pack(side='right', fill='y')
        canvas.pack(side='left', fill='both', expand=True)

        win_id = canvas.create_window((0, 0), window=self.side_inner, anchor='nw')
        self.side_inner.bind('<Configure>',
                             lambda e: canvas.configure(scrollregion=canvas.bbox('all')))
        canvas.bind('<Configure>',
                    lambda e: canvas.itemconfig(win_id, width=e.width))
        canvas.bind_all('<MouseWheel>',
                        lambda e: canvas.yview_scroll(-1 * (e.delta // 120), 'units'))

        # Tree
        tree_frame = ttk.Frame(main)
        main.add(tree_frame, weight=1)

        cols = ('name', 'size', 'mtime')
        self.tree = ttk.Treeview(tree_frame, columns=cols, show='headings',
                                  selectmode='extended')
        self.tree.heading('name', text='Nombre  ▲',
                          command=lambda: self._sort_by('name'))
        self.tree.heading('size', text='Tamaño',
                          command=lambda: self._sort_by('size'))
        self.tree.heading('mtime', text='Modificado',
                          command=lambda: self._sort_by('mtime'))
        self.tree.column('name', width=560, anchor='w')
        self.tree.column('size', width=120, anchor='e')
        self.tree.column('mtime', width=170, anchor='center')

        self.tree.tag_configure('dir', foreground='#4fc3f7')
        self.tree.tag_configure('file', foreground=C['fg'])
        self.tree.tag_configure('odd', background=C['bg_alt'])
        self.tree.tag_configure('even', background=C['row_alt'])

        vsb2 = ttk.Scrollbar(tree_frame, orient='vertical', command=self.tree.yview)
        self.tree.configure(yscrollcommand=vsb2.set)
        self.tree.pack(side='left', fill='both', expand=True)
        vsb2.pack(side='right', fill='y')

        self.tree.bind('<Double-1>', self._on_double_click)
        self.tree.bind('<Return>', self._on_enter)
        self.tree.bind('<Button-3>', self._on_right_click)
        self.tree.bind('<Delete>', lambda e: self.delete_selected())
        self.tree.bind('<BackSpace>', lambda e: self.go_up())
        self.tree.bind('<Alt-Left>', lambda e: self.go_back())
        self.tree.bind('<Alt-Right>', lambda e: self.go_forward())
        self.tree.bind('<Alt-Up>', lambda e: self.go_up())
        self.tree.bind('<<TreeviewSelect>>', lambda e: self._update_sel_info())

        # Context menu
        self.ctx = tk.Menu(self.root, tearoff=0, bg=C['bg_light'], fg=C['fg'],
                            activebackground=C['accent'], activeforeground='white',
                            bd=0, font=('Segoe UI', 9))
        self.ctx.add_command(label='  ⬇️  Descargar', command=self.download_selected)
        self.ctx.add_command(label='  📂  Descargar carpeta', command=self.download_selected)
        self.ctx.add_separator()
        self.ctx.add_command(label='  ✎  Renombrar', command=self.rename_selected)
        self.ctx.add_command(label='  🗑  Eliminar', command=self.delete_selected)
        self.ctx.add_separator()
        self.ctx.add_command(label='  📋  Copiar ruta', command=self.copy_path)

        # ===== Progress =====
        pf = ttk.Frame(self.root)
        pf.pack(fill='x', padx=12, pady=(2, 2))
        self.prog_var = tk.DoubleVar(value=0)
        self.prog = ttk.Progressbar(pf, variable=self.prog_var, maximum=100)
        self.prog.pack(side='left', fill='x', expand=True)
        self.prog_lbl = ttk.Label(pf, text='', width=52, anchor='e',
                                   style='Dim.TLabel', font=('Consolas', 8))
        self.prog_lbl.pack(side='right', padx=6)
        self.btn_cancel = ttk.Button(pf, text='✕ Cancelar',
                                      command=self._cancel_transfer, state='disabled')
        self.btn_cancel.pack(side='right', padx=4)

        # ===== Status =====
        sb = tk.Frame(self.root, bg=C['bg_dark'], height=26)
        sb.pack(fill='x', side='bottom')
        sb.pack_propagate(False)
        self.status_var = tk.StringVar(value='Listo')
        tk.Label(sb, textvariable=self.status_var, bg=C['bg_dark'],
                 fg=C['fg'], anchor='w', padx=10).pack(side='left', fill='x', expand=True)
        self.sel_info = tk.StringVar(value='')
        tk.Label(sb, textvariable=self.sel_info, bg=C['bg_dark'],
                 fg=C['success'], padx=10).pack(side='right')

        # Atajos globales
        self.root.bind('<F5>', lambda e: self.connect())
        self.root.bind('<F6>', lambda e: self.refresh())
        self.root.bind('<Control-u>', lambda e: self.upload_file())
        self.root.bind('<Control-n>', lambda e: self.mkdir())
        self.root.bind('<Control-f>', lambda e: self._focus_search())
        self.root.bind('<F2>', lambda e: self.rename_selected())
        self.root.bind('<Escape>', lambda e: self._cancel_transfer())

    def _focus_search(self):
        # Poner el foco en el entry de busqueda
        for w in self.root.winfo_children():
            pass
        # Simplificamos: usamos el propio search_var para poner foco al primer entry
        # con textvariable == search_var
        def find(w):
            for c in w.winfo_children():
                if isinstance(c, ttk.Entry):
                    try:
                        if str(c.cget('textvariable')) == str(self.search_var):
                            c.focus_set()
                            return True
                    except Exception:
                        pass
                if find(c):
                    return True
            return False
        find(self.root)

    # ---------------- SETTINGS ----------------
    def _restore_settings(self):
        s = load_settings()
        if 'host' in s: self.host_var.set(s['host'])
        if 'port' in s: self.port_var.set(s['port'])
        if 'geometry' in s:
            try: self.root.geometry(s['geometry'])
            except Exception: pass

    def _save_settings(self):
        save_settings({
            'host': self.host_var.get(),
            'port': self.port_var.get(),
            'geometry': self.root.geometry(),
        })

    # ---------------- PROTOCOL ----------------
    def _send_frame(self, data):
        h = struct.pack(HEADER_FMT, MAGIC, PROTO_VERSION, 0, len(data))
        self.sock.sendall(h + data)

    def _recv_exact(self, n):
        buf = b''
        while len(buf) < n:
            chunk = self.sock.recv(n - len(buf))
            if not chunk:
                return None
            buf += chunk
        return buf

    def _recv_frame(self):
        h = self._recv_exact(HEADER_SIZE)
        if h is None: return None
        _, _, flags, length = struct.unpack(HEADER_FMT, h)
        payload = self._recv_exact(length) if length else b''
        if payload is None: return None
        if flags & FLAG_COMPRESSED:
            payload = zlib.decompress(payload)
        return payload

    def _send_msg(self, obj):
        data = pickle.dumps(obj)
        if len(data) > COMPRESS_THRESHOLD:
            comp = zlib.compress(data, 6)
            if len(comp) < len(data):
                h = struct.pack(HEADER_FMT, MAGIC, PROTO_VERSION,
                                FLAG_COMPRESSED, len(comp))
                self.sock.sendall(h + comp)
                return
        self._send_frame(data)

    def _recv_msg(self):
        d = self._recv_frame()
        return pickle.loads(d) if d else None

    # ---------------- QUEUE ----------------
    def _process_queue(self):
        try:
            while True:
                fn, args = self.msg_queue.get_nowait()
                try:
                    fn(*args)
                except Exception as ex:
                    print('queue cb error:', repr(ex))
                    traceback.print_exc()
        except queue.Empty:
            pass
        self.root.after(60, self._process_queue)

    def post(self, fn, *args):
        self.msg_queue.put((fn, args))

    # ---------------- CONNECT ----------------
    def connect(self):
        if self.connected: return
        host = self.host_var.get().strip()
        try:
            port = int(self.port_var.get())
        except ValueError:
            messagebox.showerror('Error', 'Puerto inválido')
            return
        pw = self.pass_var.get()
        if not pw:
            messagebox.showwarning('Aviso', 'Escribe la contraseña')
            return

        self.btn_conn.config(state='disabled')
        self.conn_ind.config(text='● Conectando...', fg=C['warn'])
        self.status_var.set(f'Conectando a {host}:{port}...')
        threading.Thread(target=self._do_connect,
                         args=(host, port, pw), daemon=True).start()

    def _do_connect(self, host, port, pw):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(10)
            s.connect((host, port))
            s.settimeout(30)
            self.sock = s

            self._send_msg({'cmd': 'hello', 'version': PROTO_VERSION})
            r = self._recv_msg()
            if not r or r.get('status') != 'ok':
                raise ConnectionError(r.get('msg', 'Servidor rechazó') if r else 'Sin respuesta')

            self._send_msg({'cmd': 'auth', 'password': pw})
            a = self._recv_msg()
            if not a or a.get('status') != 'ok':
                raise ConnectionError(a.get('msg', 'Auth fallida') if a else 'Sin respuesta')

            self.token = a['token']
            self.root_name = a.get('root_name', '')
            self.sock.settimeout(None)
            self.connected = True

            # Cargar quick access
            self._send_msg({'cmd': 'quick', 'token': self.token})
            q = self._recv_msg()
            if q and q.get('status') == 'ok':
                self.quick_data = {'drives': q.get('drives', []),
                                    'user': q.get('user', [])}

            self.post(self._on_connected)
            self.current_path = ''
            self.history = ['']
            self.hist_idx = 0
            self.post(self.refresh)
        except Exception as ex:
            err = f'{type(ex).__name__}: {ex}'
            print('connect err:', err)
            traceback.print_exc()
            try:
                if self.sock: self.sock.close()
            except Exception: pass
            self.sock = None
            self.connected = False
            self.post(lambda m=err: messagebox.showerror('Error de conexión', m))
            self.post(lambda: self.conn_ind.config(text='● Desconectado', fg=C['error']))
            self.post(lambda: self.status_var.set('Desconectado'))
            self.post(lambda: self.btn_conn.config(state='normal'))

    def _on_connected(self):
        self.btn_conn.config(state='disabled', text='Conectado')
        self.btn_disc.config(state='normal')
        for b in (self.btn_ref, self.btn_ul, self.btn_mk, self.btn_rn,
                  self.btn_del, self.btn_dl, self.btn_stats,
                  self.btn_back, self.btn_fwd, self.btn_up):
            b.config(state='normal')
        self.conn_ind.config(text='● Conectado', fg=C['success'])
        self.status_var.set(f'Conectado a {self.host_var.get()}:{self.port_var.get()}')
        self._rebuild_sidebar()
        self._save_settings()

    def disconnect(self):
        if self.sock:
            try:
                self._send_msg({'cmd': 'bye', 'token': self.token})
            except Exception: pass
            try: self.sock.close()
            except Exception: pass
        self.sock = None
        self.connected = False
        self.token = None
        self.all_items = []
        self.quick_data = {'drives': [], 'user': []}
        self.history = []
        self.hist_idx = -1

        self.btn_conn.config(state='normal', text='Conectar')
        self.btn_disc.config(state='disabled')
        for b in (self.btn_ref, self.btn_ul, self.btn_mk, self.btn_rn,
                  self.btn_del, self.btn_dl, self.btn_stats,
                  self.btn_back, self.btn_fwd, self.btn_up):
            b.config(state='disabled')

        self.tree.delete(*self.tree.get_children())
        self._rebuild_sidebar()
        self.conn_ind.config(text='● Desconectado', fg=C['error'])
        self.stats_lbl.config(text='')
        self.status_var.set('Desconectado')

    def on_close(self):
        self._save_settings()
        self.disconnect()
        self.root.destroy()

    # ---------------- SIDEBAR ----------------
    def _rebuild_sidebar(self):
        for w in self.side_inner.winfo_children():
            w.destroy()

        if not self.connected:
            tk.Label(self.side_inner,
                     text='Conéctate para ver\naccesos rápidos',
                     bg=C['sidebar'], fg=C['fg_dim'],
                     font=('Segoe UI', 9), justify='left').pack(
                         anchor='w', padx=14, pady=10)
            return

        def add_section(title):
            tk.Label(self.side_inner, text=title, bg=C['sidebar'],
                     fg=C['accent'], font=('Segoe UI', 8, 'bold')).pack(
                         anchor='w', padx=14, pady=(12, 4))

        def add_item(label, path):
            def go():
                self._navigate(path, add_history=True)
            b = ttk.Button(self.side_inner, text='  ' + label,
                           style='Side.TButton', command=go)
            b.pack(fill='x', padx=6, pady=1)

        if self.quick_data.get('drives'):
            add_section('EQUIPO')
            for d in self.quick_data['drives']:
                add_item(d['label'], d['path'])

        if self.quick_data.get('user'):
            add_section('ACCESO RÁPIDO')
            for d in self.quick_data['user']:
                add_item(d['label'], d['path'])

    # ---------------- NAVIGATION ----------------
    def _navigate(self, path, add_history=True, refresh=True):
        self.current_path = path or ''
        if add_history:
            if self.hist_idx < len(self.history) - 1:
                self.history = self.history[:self.hist_idx + 1]
            if not self.history or self.history[-1] != self.current_path:
                self.history.append(self.current_path)
                self.hist_idx = len(self.history) - 1
        self._update_nav_buttons()
        self._update_breadcrumb()
        if refresh:
            self.refresh()

    def _update_nav_buttons(self):
        self.btn_back.config(state='normal' if self.hist_idx > 0 and self.connected else 'disabled')
        self.btn_fwd.config(state='normal' if self.hist_idx < len(self.history) - 1 and self.connected else 'disabled')
        self.btn_up.config(state='normal' if self.current_path and self.connected else 'disabled')

    def go_back(self):
        if self.hist_idx > 0:
            self.hist_idx -= 1
            self._navigate(self.history[self.hist_idx], add_history=False)

    def go_forward(self):
        if self.hist_idx < len(self.history) - 1:
            self.hist_idx += 1
            self._navigate(self.history[self.hist_idx], add_history=False)

    def go_up(self):
        if not self.current_path:
            return
        parts = self.current_path.split('/')
        parts.pop()
        self._navigate('/'.join(parts))

    def _update_breadcrumb(self):
        for w in self.crumb_frame.winfo_children():
            w.destroy()

        parts = self.current_path.split('/') if self.current_path else []
        root_label = f'💽 {self.root_name}' if self.root_name else '💽 Raíz'

        def make_btn(text, path):
            def go(p=path):
                self._navigate(p)
            b = ttk.Button(self.crumb_frame, text=text, style='Crumb.TButton',
                           command=go)
            b.pack(side='left', padx=1)
            return b

        make_btn(root_label, '')

        accum = ''
        for p in parts:
            accum = f'{accum}/{p}'.lstrip('/') if accum else p
            tk.Label(self.crumb_frame, text='›', bg=C['bg'], fg=C['fg_dim'],
                     font=('Segoe UI', 11, 'bold')).pack(side='left', padx=2)
            make_btn(p, accum)

    # ---------------- LIST ----------------
    def refresh(self):
        if not self.connected: return
        path = self.current_path
        threading.Thread(target=self._do_list, args=(path,), daemon=True).start()

    def _do_list(self, path):
        try:
            with self.io_lock:
                self._send_msg({'cmd': 'list', 'token': self.token, 'path': path})
                resp = self._recv_msg()
            if not resp or resp.get('status') != 'ok':
                msg = resp.get('msg', 'Error') if resp else 'Sin respuesta'
                self.post(lambda m=msg: messagebox.showerror('Error', m))
                return
            self.all_items = resp['items']
            self.post(self._apply_filter)
        except Exception as ex:
            err = f'{type(ex).__name__}: {ex}'
            print('list err:', err)
            traceback.print_exc()
            self.post(lambda m=err: messagebox.showerror('Error al listar', m))

    def _apply_filter(self):
        q = self.search_var.get().strip().lower()
        items = self.all_items
        if q:
            items = [it for it in items if q in it['name'].lower()]
        self._render_list(items)

    def _sort_by(self, col):
        if self.sort_col == col:
            self.sort_rev = not self.sort_rev
        else:
            self.sort_col = col
            self.sort_rev = False
        self._apply_filter()

    def _render_list(self, items):
        prev = set(self.tree.selection())
        self.tree.delete(*self.tree.get_children())

        col = self.sort_col
        rev = self.sort_rev

        def key(it):
            if col == 'name':
                return (not it['is_dir'], it['name'].lower())
            if col == 'size':
                return (not it['is_dir'], it['size'])
            if col == 'mtime':
                return (not it['is_dir'], it['mtime'])
            return it['name'].lower()

        items = sorted(items, key=key, reverse=rev)

        for i, it in enumerate(items):
            icon = file_icon(it['name'], it['is_dir'])
            size = '—' if it['is_dir'] else human_size(it['size'])
            tags = ['dir' if it['is_dir'] else 'file', 'odd' if i % 2 else 'even']
            self.tree.insert('', 'end', iid=it['name'],
                             values=(f'{icon}  {it["name"]}', size,
                                     fmt_date(it['mtime'])),
                             tags=tuple(tags))

        for n in prev:
            if self.tree.exists(n):
                self.tree.selection_add(n)

        for c, txt in (('name', 'Nombre'), ('size', 'Tamaño'),
                       ('mtime', 'Modificado')):
            suffix = ''
            if c == self.sort_col:
                suffix = '  ▼' if rev else '  ▲'
            self.tree.heading(c, text=txt + suffix)

        total = len(self.all_items)
        shown = len(items)
        path_lbl = self.current_path or '/'
        if shown == total:
            self.status_var.set(f'{shown} elemento(s) · /{path_lbl}')
        else:
            self.status_var.set(f'{shown} de {total} elemento(s) filtrados')
        self._update_sel_info()

    def _update_sel_info(self):
        sel = self.tree.selection()
        if not sel:
            self.sel_info.set('')
            return
        total = 0
        dirs = 0
        for name in sel:
            for it in self.all_items:
                if it['name'] == name:
                    if it['is_dir']:
                        dirs += 1
                    else:
                        total += it['size']
                    break
        if len(sel) == 1:
            for it in self.all_items:
                if it['name'] == sel[0]:
                    if it['is_dir']:
                        self.sel_info.set(f'📁 {it["name"]}')
                    else:
                        self.sel_info.set(f'📄 {human_size(it["size"])}')
                    return
        else:
            self.sel_info.set(f'{len(sel)} sel · {human_size(total)}')

    # ---------------- SELECTION ----------------
    def _selected(self):
        return list(self.tree.selection())

    def _on_double_click(self, e):
        sel = self._selected()
        if not sel: return
        name = sel[0]
        for it in self.all_items:
            if it['name'] == name and it['is_dir']:
                new_path = f'{self.current_path}/{name}'.lstrip('/')
                self._navigate(new_path)
                return

    def _on_enter(self, e):
        self._on_double_click(e)

    def _on_right_click(self, e):
        row = self.tree.identify_row(e.y)
        if row:
            if row not in self.tree.selection():
                self.tree.selection_set(row)
            self.ctx.tk_popup(e.x_root, e.y_root)

    def copy_path(self):
        sel = self._selected()
        if not sel: return
        path = f'{self.current_path}/{sel[0]}'.lstrip('/')
        self.root.clipboard_clear()
        self.root.clipboard_append(path)
        self.status_var.set(f'Ruta copiada: {path}')

    # ---------------- DOWNLOAD ----------------
    def download_selected(self):
        sel = self._selected()
        if not sel:
            messagebox.showwarning('Aviso', 'Selecciona al menos un elemento')
            return
        if self.transfer_busy:
            messagebox.showwarning('Aviso', 'Ya hay una transferencia en curso')
            return

        # Clasificar archivos y carpetas
        files = []
        folders = []
        for name in sel:
            for it in self.all_items:
                if it['name'] == name:
                    (folders if it['is_dir'] else files).append(name)
                    break

        dest = filedialog.askdirectory(title='Carpeta destino')
        if not dest:
            return

        self.transfer_cancel = False
        self.transfer_busy = True
        self.btn_cancel.config(state='normal')
        threading.Thread(target=self._do_download_multi,
                         args=(files, folders, dest), daemon=True).start()

    def _do_download_multi(self, files, folders, dest):
        try:
            ok, fail = 0, 0
            for name in files:
                if self.transfer_cancel: break
                if self._dl_file(name, dest):
                    ok += 1
                else:
                    fail += 1
            for name in folders:
                if self.transfer_cancel: break
                if self._dl_folder(name, dest):
                    ok += 1
                else:
                    fail += 1

            if self.transfer_cancel:
                self.post(lambda: self.status_var.set(
                    f'Cancelado · {ok} completados'))
            else:
                self.post(lambda o=ok, f=fail: messagebox.showinfo(
                    'Listo', f'Completado\n✔ {o}  ✘ {f}'))
        finally:
            self.transfer_busy = False
            self.post(self._reset_prog)
            self.post(lambda: self.btn_cancel.config(state='disabled'))

    def _dl_file(self, name, dest):
        rel = f'{self.current_path}/{name}'.lstrip('/')
        try:
            with self.io_lock:
                self._send_msg({'cmd': 'download', 'token': self.token, 'path': rel})
                r = self._recv_msg()
                if not r or r.get('status') != 'ok':
                    msg = r.get('msg', 'Error') if r else 'Sin respuesta'
                    self.post(lambda m=msg: messagebox.showerror('Error', m))
                    return False
                size = r['size']
                save = unique_path(os.path.join(dest, r['name']))
                received = 0
                t0 = time.time()
                with open(save, 'wb') as f:
                    while received < size:
                        if self.transfer_cancel:
                            break
                        chunk = self._recv_frame()
                        if chunk is None:
                            raise ConnectionError('Conexión cerrada')
                        f.write(chunk)
                        received += len(chunk)
                        pct = received * 100 / size if size else 100
                        el = max(time.time() - t0, 0.001)
                        sp = received / el
                        eta = (size - received) / sp if sp > 0 else 0
                        self.post(self._upd_prog, pct,
                                  f'⬇ {r["name"]} · {human_size(received)}/{human_size(size)} · '
                                  f'{human_size(int(sp))}/s · ETA {human_time(eta)}')
            if received < size:
                try: os.remove(save)
                except Exception: pass
                return False
            return True
        except Exception as ex:
            err = f'{type(ex).__name__}: {ex}'
            print('dl file err:', err)
            traceback.print_exc()
            self.post(lambda m=err: messagebox.showerror('Error descarga', m))
            return False

    def _dl_folder(self, name, dest):
        rel = f'{self.current_path}/{name}'.lstrip('/')
        try:
            with self.io_lock:
                self._send_msg({'cmd': 'download_folder',
                                'token': self.token, 'path': rel})
                manifest = self._recv_msg()
                if not manifest or manifest.get('status') != 'ok':
                    msg = manifest.get('msg', 'Error') if manifest else 'Sin respuesta'
                    self.post(lambda m=msg: messagebox.showerror('Error', m))
                    return False

                total_files = manifest['total_files']
                total_size = manifest['total_size']
                folder_name = manifest['name']
                base_dest = unique_path(os.path.join(dest, folder_name))

                received_total = 0
                file_i = 0
                t0 = time.time()

                while True:
                    if self.transfer_cancel:
                        # drenar: leer mensajes hasta done
                        try:
                            self._send_msg({'cmd': 'bye', 'token': self.token})
                        except Exception:
                            pass
                        return False

                    hdr = self._recv_msg()
                    if not hdr:
                        raise ConnectionError('Conexión cerrada')
                    kind = hdr.get('kind')
                    if kind == 'done':
                        break
                    if kind != 'file_start':
                        continue

                    frel = hdr['rel']
                    fsize = hdr['size']
                    out = os.path.join(base_dest, *frel.split('/'))
                    os.makedirs(os.path.dirname(out), exist_ok=True)

                    received = 0
                    with open(out, 'wb') as f:
                        while received < fsize:
                            if self.transfer_cancel:
                                break
                            chunk = self._recv_frame()
                            if chunk is None:
                                raise ConnectionError('Conexión cerrada')
                            if not chunk and received < fsize:
                                # archivo con error en server, saltar
                                break
                            f.write(chunk)
                            received += len(chunk)
                            received_total += len(chunk)
                            pct = received_total * 100 / total_size if total_size else 100
                            el = max(time.time() - t0, 0.001)
                            sp = received_total / el
                            eta = (total_size - received_total) / sp if sp > 0 else 0
                            self.post(self._upd_prog, pct,
                                      f'⬇ {folder_name} · {file_i+1}/{total_files} · '
                                      f'{human_size(received_total)}/{human_size(total_size)} · '
                                      f'{human_size(int(sp))}/s · ETA {human_time(eta)}')
                    file_i += 1

            return True
        except Exception as ex:
            err = f'{type(ex).__name__}: {ex}'
            print('dl folder err:', err)
            traceback.print_exc()
            self.post(lambda m=err: messagebox.showerror('Error descarga carpeta', m))
            return False

    # ---------------- UPLOAD ----------------
    def upload_file(self):
        if not self.connected or self.transfer_busy: return
        paths = filedialog.askopenfilenames(title='Selecciona archivos a subir')
        if not paths: return
        self.transfer_cancel = False
        self.transfer_busy = True
        self.btn_cancel.config(state='normal')
        threading.Thread(target=self._do_upload_multi,
                         args=(paths,), daemon=True).start()

    def _do_upload_multi(self, paths):
        try:
            ok, fail = 0, 0
            for p in paths:
                if self.transfer_cancel: break
                if self._ul_file(p): ok += 1
                else: fail += 1
            if not self.transfer_cancel:
                self.post(lambda o=ok, f=fail: messagebox.showinfo(
                    'Listo', f'Subida completada\n✔ {o}  ✘ {f}'))
            self.post(self.refresh)
        finally:
            self.transfer_busy = False
            self.post(self._reset_prog)
            self.post(lambda: self.btn_cancel.config(state='disabled'))

    def _ul_file(self, path):
        name = os.path.basename(path)
        size = os.path.getsize(path)
        rel = f'{self.current_path}/{name}'.lstrip('/')
        try:
            with self.io_lock:
                self._send_msg({'cmd': 'upload', 'token': self.token,
                                'path': rel, 'size': size})
                r = self._recv_msg()
                if not r or r.get('status') != 'ok':
                    msg = r.get('msg', 'Error') if r else 'Sin respuesta'
                    self.post(lambda m=msg: messagebox.showerror('Error', m))
                    return False

                sent = 0
                t0 = time.time()
                with open(path, 'rb') as f:
                    while sent < size:
                        if self.transfer_cancel: break
                        chunk = f.read(CHUNK_SIZE)
                        if not chunk: break
                        self._send_frame(chunk)
                        sent += len(chunk)
                        pct = sent * 100 / size if size else 100
                        el = max(time.time() - t0, 0.001)
                        sp = sent / el
                        eta = (size - sent) / sp if sp > 0 else 0
                        self.post(self._upd_prog, pct,
                                  f'⬆ {name} · {human_size(sent)}/{human_size(size)} · '
                                  f'{human_size(int(sp))}/s · ETA {human_time(eta)}')
                if self.transfer_cancel: return False
                r2 = self._recv_msg()
                if not r2 or r2.get('status') != 'ok':
                    return False
            return True
        except Exception as ex:
            err = f'{type(ex).__name__}: {ex}'
            print('ul err:', err)
            traceback.print_exc()
            self.post(lambda m=err: messagebox.showerror('Error subida', m))
            return False

    # ---------------- OPS ----------------
    def mkdir(self):
        if not self.connected: return
        name = simpledialog.askstring('Nueva carpeta', 'Nombre:')
        if not name: return
        rel = f'{self.current_path}/{name}'.lstrip('/')
        threading.Thread(target=self._simple_op,
                         args=('mkdir', {'path': rel}), daemon=True).start()

    def rename_selected(self):
        sel = self._selected()
        if len(sel) != 1:
            messagebox.showwarning('Aviso', 'Selecciona exactamente un elemento')
            return
        old = sel[0]
        new = simpledialog.askstring('Renombrar', f'Nuevo nombre para "{old}":',
                                      initialvalue=old)
        if not new or new == old: return
        ro = f'{self.current_path}/{old}'.lstrip('/')
        rn = f'{self.current_path}/{new}'.lstrip('/')
        threading.Thread(target=self._simple_op,
                         args=('rename', {'old': ro, 'new': rn}), daemon=True).start()

    def delete_selected(self):
        sel = self._selected()
        if not sel: return
        if not messagebox.askyesno('Confirmar',
                                    f'¿Eliminar {len(sel)} elemento(s)?\n\n'
                                    f'{", ".join(sel[:5])}' +
                                    ('...' if len(sel) > 5 else '')):
            return
        threading.Thread(target=self._del_multi, args=(sel,), daemon=True).start()

    def _del_multi(self, names):
        for name in names:
            rel = f'{self.current_path}/{name}'.lstrip('/')
            try:
                with self.io_lock:
                    self._send_msg({'cmd': 'delete', 'token': self.token, 'path': rel})
                    r = self._recv_msg()
                if not r or r.get('status') != 'ok':
                    msg = r.get('msg', 'Error') if r else 'Sin respuesta'
                    self.post(lambda m=msg: messagebox.showerror('Error', m))
            except Exception as ex:
                err = f'{type(ex).__name__}: {ex}'
                self.post(lambda m=err: messagebox.showerror('Error', m))
        self.post(self.refresh)

    def _simple_op(self, cmd, payload):
        try:
            with self.io_lock:
                self._send_msg({'cmd': cmd, 'token': self.token, **payload})
                r = self._recv_msg()
            if r and r.get('status') == 'ok':
                self.post(self.refresh)
            else:
                msg = r.get('msg', 'Error') if r else 'Sin respuesta'
                self.post(lambda m=msg: messagebox.showerror('Error', m))
        except Exception as ex:
            err = f'{type(ex).__name__}: {ex}'
            self.post(lambda m=err: messagebox.showerror('Error', m))

    def show_stats(self):
        if not self.connected: return
        threading.Thread(target=self._do_stats, daemon=True).start()

    def _do_stats(self):
        try:
            with self.io_lock:
                self._send_msg({'cmd': 'stats', 'token': self.token})
                r = self._recv_msg()
            if not r or r.get('status') != 'ok':
                msg = r.get('msg', 'Error') if r else 'Sin respuesta'
                self.post(lambda m=msg: messagebox.showerror('Error', m))
                return
            self.post(self._show_stats_win, r)
            self.post(lambda s=r: self.stats_lbl.config(
                text=f'⏱ {human_time(s["uptime"])}  ·  📄 {s["files"]:,}  ·  '
                     f'💾 {human_size(s["bytes"])}  ·  👥 {s["clients"]}'))
        except Exception as ex:
            err = f'{type(ex).__name__}: {ex}'
            self.post(lambda m=err: messagebox.showerror('Error', m))

    def _show_stats_win(self, s):
        w = tk.Toplevel(self.root)
        w.title('Estadísticas del servidor')
        w.configure(bg=C['bg'])
        w.geometry('460x300')
        w.transient(self.root)
        tk.Label(w, text='📊  Servidor CFS1 Pro', bg=C['bg'], fg=C['accent'],
                 font=('Segoe UI', 13, 'bold')).pack(pady=12)
        f = tk.Frame(w, bg=C['bg'])
        f.pack(fill='both', expand=True, padx=24, pady=8)
        rows = [
            ('Tiempo activo', human_time(s['uptime'])),
            ('Archivos', f'{s["files"]:,}'),
            ('Tamaño total', human_size(s['bytes'])),
            ('Clientes activos', f'{s["clients"]}'),
            ('Carpeta compartida', s['path']),
        ]
        for i, (k, v) in enumerate(rows):
            tk.Label(f, text=k + ':', bg=C['bg'], fg=C['fg_dim'],
                     anchor='w', font=('Segoe UI', 9)).grid(row=i, column=0,
                                                              sticky='w', pady=5)
            tk.Label(f, text=v, bg=C['bg'], fg=C['fg'], anchor='w',
                     font=('Consolas', 9)).grid(row=i, column=1, sticky='w',
                                                 padx=12, pady=5)
        ttk.Button(w, text='Cerrar', command=w.destroy).pack(pady=12)

    # ---------------- PROGRESS ----------------
    def _upd_prog(self, pct, text):
        self.prog_var.set(pct)
        self.prog_lbl.config(text=text)

    def _reset_prog(self):
        self.prog_var.set(0)
        self.prog_lbl.config(text='')

    def _cancel_transfer(self):
        if self.transfer_busy:
            self.transfer_cancel = True
            self.status_var.set('Cancelando...')


# ==================== MAIN ====================
if __name__ == '__main__':
    root = tk.Tk()
    app = CFS1Client(root)
    root.mainloop()