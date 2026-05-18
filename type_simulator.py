import tkinter as tk
from tkinter import scrolledtext, messagebox, filedialog, font
import threading
import time
import ctypes
import ctypes.wintypes
import sys
import os
import math
import struct
import tempfile

user32 = ctypes.windll.user32
kernel32 = ctypes.windll.kernel32
shell32 = ctypes.windll.shell32

KEYEVENTF_KEYUP = 0x0002
VK_SHIFT = 0x10
VK_RETURN = 0x0D
VK_TAB = 0x09
VK_CONTROL = 0x11
VK_SPACE = 0x20

WM_DROPFILES = 0x0233
WM_NCHITTEST = 0x0084
GWL_WNDPROC = -4

HWND = ctypes.c_void_p
UINT = ctypes.c_uint
WPARAM = ctypes.c_void_p
LPARAM = ctypes.c_void_p
LRESULT = ctypes.c_void_p
HKL = ctypes.c_void_p

user32.SetWindowLongPtrW.argtypes = [HWND, ctypes.c_int, ctypes.c_void_p]
user32.SetWindowLongPtrW.restype = ctypes.c_void_p

user32.CallWindowProcW.argtypes = [ctypes.c_void_p, HWND, UINT, WPARAM, LPARAM]
user32.CallWindowProcW.restype = LRESULT

shell32.DragAcceptFiles.argtypes = [HWND, ctypes.c_bool]
shell32.DragAcceptFiles.restype = None

shell32.DragQueryFileW.argtypes = [ctypes.c_void_p, UINT, ctypes.c_wchar_p, UINT]
shell32.DragQueryFileW.restype = UINT

shell32.DragFinish.argtypes = [ctypes.c_void_p]
shell32.DragFinish.restype = None

WNDPROC_CALLBACK = ctypes.WINFUNCTYPE(LRESULT, HWND, UINT, WPARAM, LPARAM)

user32.GetForegroundWindow.argtypes = []
user32.GetForegroundWindow.restype = HWND

user32.LoadKeyboardLayoutW.argtypes = [ctypes.c_wchar_p, UINT]
user32.LoadKeyboardLayoutW.restype = HKL

user32.PostMessageW.argtypes = [HWND, UINT, WPARAM, LPARAM]
user32.PostMessageW.restype = ctypes.c_bool

user32.SetWindowPos.argtypes = [HWND, HWND, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, UINT]
user32.SetWindowPos.restype = ctypes.c_bool

HWND_BOTTOM = HWND(1)
HWND_TOP = HWND(0)
SWP_NOACTIVATE = 0x0010
SWP_NOMOVE = 0x0002
SWP_NOSIZE = 0x0001

user32.RegisterHotKey.argtypes = [HWND, ctypes.c_int, UINT, UINT]
user32.RegisterHotKey.restype = ctypes.c_bool

user32.UnregisterHotKey.argtypes = [HWND, ctypes.c_int]
user32.UnregisterHotKey.restype = ctypes.c_bool

user32.ReleaseCapture.argtypes = []
user32.ReleaseCapture.restype = ctypes.c_bool

user32.SendMessageW.argtypes = [HWND, UINT, WPARAM, LPARAM]
user32.SendMessageW.restype = LRESULT

MOD_NOREPEAT = 0x4000
WM_HOTKEY = 0x0312
WM_SYSCOMMAND = 0x0112
HOTKEY_ID = 1
HT_CAPTION = 2
SC_MOVE = 0xF010

user32.OpenClipboard.argtypes = [HWND]
user32.OpenClipboard.restype = ctypes.c_bool

user32.EmptyClipboard.argtypes = []
user32.EmptyClipboard.restype = ctypes.c_bool

user32.SetClipboardData.argtypes = [ctypes.c_uint, ctypes.c_void_p]
user32.SetClipboardData.restype = ctypes.c_void_p

user32.CloseClipboard.argtypes = []
user32.CloseClipboard.restype = ctypes.c_bool

kernel32.GlobalAlloc.argtypes = [ctypes.c_uint, ctypes.c_size_t]
kernel32.GlobalAlloc.restype = ctypes.c_void_p

kernel32.GlobalLock.argtypes = [ctypes.c_void_p]
kernel32.GlobalLock.restype = ctypes.c_void_p

kernel32.GlobalUnlock.argtypes = [ctypes.c_void_p]
kernel32.GlobalUnlock.restype = ctypes.c_bool

KLF_ACTIVATE = 0x00000001
WM_INPUTLANGCHANGEREQUEST = 0x0050
CF_UNICODETEXT = 13
GMEM_MOVABLE = 0x0002

def generate_icon():
    size = 32
    half = size // 2
    pixels = []
    for y in range(size):
        row = []
        for x in range(size):
            dx = x - half + 0.5
            dy = y - half + 0.5
            dist = math.sqrt(dx * dx + dy * dy)
            if x >= 9 and x <= 22 and y >= 18 and y <= 25:
                r, g, b, a = 15, 52, 96, 200
                if 12 <= x <= 14 and 20 <= y <= 22:
                    r, g, b, a = 233, 69, 96, 255
                if 17 <= x <= 19 and 20 <= y <= 22:
                    r, g, b, a = 233, 69, 96, 255
            elif dist < 14:
                r, g, b, a = 233, 69, 96, 180 if dist > 10 else 255
            else:
                r, g, b, a = 0, 0, 0, 0
            row.extend([b, g, r, a])
        pixels.extend(row[::-1])

    xor_size = size * size * 4
    and_size = ((size + 31) // 32) * 4 * size
    xor_data = bytes(pixels)
    and_data = b'\x00' * and_size
    data = xor_data + and_data
    data_size = len(data)
    buf = bytearray()
    buf.extend(struct.pack('<HHH', 0, 1, 1))
    buf.extend(struct.pack('<BBHHHHHHII', 32, 32, 0, 0, 1, 32, 0, 0, data_size, 22))
    buf.extend(data)

    ico_path = os.path.join(os.path.dirname(os.path.abspath(sys.argv[0]) if getattr(sys, 'frozen', False) else __file__), 'TypeSimulator.ico')
    try:
        with open(ico_path, 'wb') as f:
            f.write(bytes(buf))
    except Exception:
        pass

def load_icon_for_window(tk_window):
    try:
        exe_dir = os.path.dirname(os.path.abspath(sys.argv[0]) if getattr(sys, 'frozen', False) else __file__)
        icon_path = os.path.join(exe_dir, 'TypeSimulator.ico')
        if os.path.exists(icon_path):
            tk_window.iconbitmap(icon_path)
            return
    except Exception:
        pass

def press_key(vk_code):
    user32.keybd_event(vk_code, 0, 0, 0)

def release_key(vk_code):
    user32.keybd_event(vk_code, 0, KEYEVENTF_KEYUP, 0)

def tap_key(vk_code):
    press_key(vk_code)
    time.sleep(0.01)
    release_key(vk_code)

def send_via_clipboard(text):
    try:
        user32.OpenClipboard(None)
        user32.EmptyClipboard()
        data = (text + '\0').encode('utf-16-le')
        h_mem = kernel32.GlobalAlloc(GMEM_MOVABLE, len(data))
        if h_mem:
            p_mem = kernel32.GlobalLock(h_mem)
            if p_mem:
                ctypes.memmove(p_mem, data, len(data))
                kernel32.GlobalUnlock(h_mem)
            user32.SetClipboardData(CF_UNICODETEXT, h_mem)
        user32.CloseClipboard()
        press_key(VK_CONTROL)
        tap_key(0x56)
        release_key(VK_CONTROL)
        return True
    except Exception:
        return False

def is_ascii_printable(ch):
    return 32 <= ord(ch) <= 126

def switch_to_english():
    try:
        h_wnd = user32.GetForegroundWindow()
        us_hkl = user32.LoadKeyboardLayoutW("00000409", KLF_ACTIVATE)
        if us_hkl:
            user32.PostMessageW(h_wnd, WM_INPUTLANGCHANGEREQUEST, 0, LPARAM(us_hkl.value))
        time.sleep(0.1)
        tap_key(VK_SHIFT)
        time.sleep(0.05)
    except Exception:
        pass


class TypeApp:
    C = {
        "bg": "#06060e",
        "bar": "#0c0c1a",
        "card": "#0d1125",
        "card_edge": "#1a1f3a",
        "accent": "#e94560",
        "accent_dim": "#0f3460",
        "text": "#dde0f0",
        "text_dim": "#556688",
        "text_bright": "#ffffff",
        "green": "#39ff14",
        "yellow": "#ffc107",
        "input_bg": "#040610",
        "close_hover": "#e94560",
    }

    def __init__(self):
        self.window = tk.Tk()
        self.window.overrideredirect(True)
        self.window.configure(bg=self.C["bg"])

        sw = self.window.winfo_screenwidth()
        sh = self.window.winfo_screenheight()
        w, h = 560, 500
        self.window.geometry(f"{w}x{h}+{(sw-w)//2}+{(sh-h)//2}")

        try:
            load_icon_for_window(self.window)
        except Exception:
            pass

        self._drop_old_proc = None
        self._drop_callback = None
        self.typing_thread = None
        self.pause_event = threading.Event()
        self.typing_content = ""
        self.mode_is_english = True
        self.typing_index = 0
        self._drag_x = 0
        self._drag_y = 0

        self._build_ui()

        self.window.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.window.after(200, self._init_drop_target)
        self._load_cli_file_after_ui()
        self.window.after(500, self._register_hotkey)
        self.window.bind("<space>", self._on_space)

        try:
            generate_icon()
        except Exception:
            pass

        self.window.mainloop()

    def _start_move(self, event):
        self._drag_x = event.x
        self._drag_y = event.y

    def _do_move(self, event):
        dx = event.x - self._drag_x
        dy = event.y - self._drag_y
        x = self.window.winfo_x() + dx
        y = self.window.winfo_y() + dy
        self.window.geometry(f"+{x}+{y}")

    def _init_drop_target(self):
        try:
            hwnd = HWND(self.window.winfo_id())
            shell32.DragAcceptFiles(hwnd, True)

            def wnd_proc(h_wnd, msg, w_param, l_param):
                if msg == WM_DROPFILES:
                    self._handle_drop(w_param)
                    return LRESULT(0)
                if msg == WM_HOTKEY:
                    self.window.after(10, self._toggle_by_hotkey)
                    return LRESULT(0)
                return user32.CallWindowProcW(
                    self._drop_old_proc, h_wnd, msg, w_param, l_param
                )

            self._drop_callback = WNDPROC_CALLBACK(wnd_proc)
            self._drop_old_proc = user32.SetWindowLongPtrW(
                hwnd, GWL_WNDPROC, self._drop_callback
            )
        except Exception:
            pass

    def _handle_drop(self, h_drop):
        try:
            file_count = shell32.DragQueryFileW(h_drop, UINT(0xFFFFFFFF), None, UINT(0))
            for i in range(file_count):
                buf = ctypes.create_unicode_buffer(260)
                shell32.DragQueryFileW(h_drop, UINT(i), buf, UINT(ctypes.sizeof(buf) // 2))
                file_path = buf.value
                if file_path.lower().endswith('.txt'):
                    self.window.after(100, lambda p=file_path: self._do_load_file(p))
                    break
            shell32.DragFinish(h_drop)
        except Exception:
            pass

    def _btn(self, parent, text, command, **kw):
        bg = kw.pop('bg', self.C["accent"])
        fg = kw.pop('fg', self.C["text_bright"])
        fs = kw.pop('fs', 11)
        btn = tk.Button(
            parent, text=text, command=command,
            font=("Microsoft YaHei UI", fs),
            bg=bg, fg=fg,
            activebackground=kw.pop('abg', bg),
            activeforeground=fg,
            bd=0, highlightthickness=0,
            padx=kw.pop('px', 12),
            pady=kw.pop('py', 6),
            cursor="hand2",
            **kw
        )
        return btn

    def _lbl(self, parent, text, **kw):
        return tk.Label(
            parent, text=text,
            font=("Microsoft YaHei UI", kw.pop('size', 10), "bold" if kw.pop('bold', False) else "normal"),
            bg=kw.pop('bg', self.C["bg"]),
            fg=kw.pop('fg', self.C["text_dim"]),
            **kw
        )

    def _build_ui(self):
        self._build_drag_bar()
        self._build_header()
        self._build_separator()
        self._build_mode_switch()
        self._build_card()
        self._build_footer()
        self._update_mode_display()

    def _build_drag_bar(self):
        bar = tk.Frame(self.window, bg=self.C["bar"], height=32)
        bar.pack(fill=tk.X)
        bar.bind("<Button-1>", self._start_move)
        bar.bind("<B1-Motion>", self._do_move)

        self._lbl(bar, "  键盘打字助手", size=9, fg=self.C["text_dim"], bg=self.C["bar"]).pack(side=tk.LEFT, pady=4)

        close_btn = tk.Label(
            bar, text=" ✕ ", font=("Microsoft YaHei UI", 11),
            bg=self.C["bar"], fg=self.C["text_dim"],
            cursor="hand2"
        )
        close_btn.pack(side=tk.RIGHT, padx=4, pady=2)
        close_btn.bind("<Button-1>", lambda e: self.on_closing())
        close_btn.bind("<Enter>", lambda e: close_btn.config(bg=self.C["close_hover"], fg="white"))
        close_btn.bind("<Leave>", lambda e: close_btn.config(bg=self.C["bar"], fg=self.C["text_dim"]))

    def _build_header(self):
        hf = tk.Frame(self.window, bg=self.C["bg"])
        hf.pack(fill=tk.X, pady=(18, 0))

        tk.Label(
            hf, text="⌨️ 键盘打字助手",
            font=("Microsoft YaHei UI", 18, "bold"),
            bg=self.C["bg"], fg=self.C["accent"]
        ).pack()

        tk.Label(
            hf, text="输入或导入文本  ·  模拟键盘逐字输出",
            font=("Microsoft YaHei UI", 9),
            bg=self.C["bg"], fg=self.C["text_dim"]
        ).pack(pady=(2, 0))

    def _build_separator(self):
        sep = tk.Canvas(self.window, height=1, bg=self.C["bg"], highlightthickness=0)
        sep.pack(fill=tk.X, padx=36, pady=(10, 8))
        sep.create_line(0, 0, 560, 0, fill=self.C["accent"], width=1)

    def _build_mode_switch(self):
        mr = tk.Frame(self.window, bg=self.C["bg"])
        mr.pack(pady=(0, 6))

        self.mode_btn = self._btn(
            mr, "🔤  英文模式", self.toggle_mode,
            bg=self.C["accent_dim"], fs=10, px=18, py=5
        )
        self.mode_btn.pack()

    def _build_card(self):
        card = tk.Frame(
            self.window, bg=self.C["card"],
            highlightbackground=self.C["card_edge"],
            highlightthickness=1
        )
        card.pack(fill=tk.BOTH, expand=True, padx=24, pady=2)

        inner = tk.Frame(card, bg=self.C["card"])
        inner.pack(fill=tk.BOTH, expand=True, padx=1, pady=1)

        lr = tk.Frame(inner, bg=self.C["card"])
        lr.pack(fill=tk.X, padx=14, pady=(10, 4))

        self._lbl(lr, "输入内容", size=11, fg=self.C["text"], bold=True, bg=self.C["card"]).pack(side=tk.LEFT)

        self.file_btn = self._btn(
            lr, "📂  选择文本文档", self.load_text_file,
            bg=self.C["accent_dim"], fs=9, px=10, py=2
        )
        self.file_btn.pack(side=tk.RIGHT)

        self.text_area = scrolledtext.ScrolledText(
            inner, wrap=tk.WORD,
            font=("Microsoft YaHei UI", 11),
            bg=self.C["input_bg"], fg=self.C["text"],
            insertbackground=self.C["accent"],
            bd=0, highlightthickness=0,
            height=8, padx=12, pady=12
        )
        self.text_area.pack(fill=tk.BOTH, expand=True, padx=12, pady=(0, 10))

    def _build_footer(self):
        info = tk.Frame(self.window, bg=self.C["bg"])
        info.pack(fill=tk.X, padx=24, pady=(2, 0))

        self.info_label = self._lbl(info, "", size=8, fg=self.C["text_dim"])
        self.info_label.pack(anchor=tk.W)

        self.status_label = self._lbl(info, "", size=9, fg=self.C["accent"])
        self.status_label.pack(anchor=tk.W)

        self.btn_container = tk.Frame(self.window, bg=self.C["bg"])
        self.btn_container.pack(fill=tk.X, padx=24, pady=(6, 12))

        self.confirm_btn = self._btn(
            self.btn_container, "▶  开始打字", self.toggle_typing,
            bg=self.C["accent"], fs=14, px=20, py=12
        )
        self.confirm_btn.pack(fill=tk.X)

        self.pause_frame = tk.Frame(self.btn_container, bg=self.C["bg"])

        btn_continue = self._btn(
            self.pause_frame, "▶  从断点继续", self._resume_from_here,
            bg="#27ae60", fs=14, px=20, py=12
        )
        btn_continue.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 3))

        btn_restart = self._btn(
            self.pause_frame, "🔄  从头开始", self._restart_from_beginning,
            bg="#e67e22", fs=14, px=20, py=12
        )
        btn_restart.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(3, 0))

    def _on_space(self, event):
        if self.typing_thread and self.typing_thread.is_alive():
            if self.pause_event.is_set():
                self._resume_typing()
            else:
                self.pause_typing()

    def _toggle_by_hotkey(self):
        if self.typing_thread and self.typing_thread.is_alive():
            if self.pause_event.is_set():
                self._resume_typing()
            else:
                self.pause_typing()

    def _register_hotkey(self):
        try:
            hwnd = HWND(self.window.winfo_id())
            user32.RegisterHotKey(hwnd, HOTKEY_ID, MOD_NOREPEAT, VK_SPACE)
        except Exception:
            pass

    def _unregister_hotkey(self):
        try:
            hwnd = HWND(self.window.winfo_id())
            user32.UnregisterHotKey(hwnd, HOTKEY_ID)
        except Exception:
            pass

    def _resume_typing(self):
        self._resume_from_here()

    def _resume_from_here(self):
        self._show_main_button()
        self.pause_event.clear()
        self.confirm_btn.config(text="⏸  暂停 · 空格", bg="#d4880f", activebackground="#d4880f")
        self.status_label.config(text="⏳ 倒计时中...", fg=self.C["yellow"])
        self.text_area.config(state="normal")
        self.typing_thread = threading.Thread(target=self._resume_countdown, daemon=True)
        self.typing_thread.start()

    def _restart_from_beginning(self):
        self.typing_index = 0
        self._resume_from_here()

    def _resume_countdown(self):
        for i in range(3, 0, -1):
            if self.pause_event.is_set():
                self.window.after(0, self._restore_text_area_resume)
                return
            self.window.after(0, lambda n=i: self._show_count_in_text(n))
            time.sleep(1)
        if self.pause_event.is_set():
            self.window.after(0, self._restore_text_area_resume)
            return
        self.window.after(0, self._show_go_in_text)
        time.sleep(0.6)
        self.window.after(0, self._begin_typing_resume)

    def _begin_typing_resume(self):
        self.text_area.config(state="normal")
        self.text_area.config(font=("Microsoft YaHei UI", 11), fg=self.C["text"])
        self.text_area.delete("1.0", tk.END)
        for tag in self.text_area.tag_names():
            self.text_area.tag_delete(tag)
        self.text_area.insert("1.0", self.typing_content)
        self.text_area.config(state="disabled")
        self.text_area.see("1.0")
        self.status_label.config(text="▶ 打字进行中...", fg=self.C["green"])
        self._send_to_bottom()
        self.typing_thread = threading.Thread(target=self._run_typing, daemon=True)
        self.typing_thread.start()

    def _restore_text_area_resume(self):
        self.text_area.config(font=("Microsoft YaHei UI", 11), fg=self.C["text"])
        self.text_area.delete("1.0", tk.END)
        self.text_area.insert("1.0", self.typing_content)
        self.text_area.config(state="disabled")

    def _send_to_bottom(self):
        try:
            self.window.lower()
        except Exception:
            pass

    def _bring_to_top(self):
        self.window.deiconify()
        self.window.lift()

    def _update_mode_display(self):
        if self.mode_is_english:
            self.mode_btn.config(text="🔤  英文模式")
            self.info_label.config(text="英文模式 · 英文字母/数字/符号 · 自动切换英文输入法 · 空格键暂停/继续")
        else:
            self.mode_btn.config(text="🀄  中文模式")
            self.info_label.config(text="中文模式 · 中文/英文/数字/符号 · 空格键暂停/继续")

    def toggle_mode(self):
        if self.typing_thread and self.typing_thread.is_alive():
            messagebox.showwarning("提示", "请先暂停或等待打字完成后再切换模式！")
            return
        self.mode_is_english = not self.mode_is_english
        self._update_mode_display()

    def _load_cli_file_after_ui(self):
        if len(sys.argv) > 1:
            fp = sys.argv[1]
            if os.path.isfile(fp) and fp.lower().endswith('.txt'):
                self.window.after(300, lambda: self._do_load_file(fp))

    def load_text_file(self):
        fp = filedialog.askopenfilename(
            title="选择文本文档",
            filetypes=[("文本文件", "*.txt"), ("所有文件", "*.*")]
        )
        if not fp:
            return
        self._do_load_file(fp)

    def _do_load_file(self, fp):
        if self.typing_thread and self.typing_thread.is_alive():
            self.pause_event.set()
            self.typing_thread = None
        self._reset_buttons()
        try:
            with open(fp, "r", encoding="utf-8") as f:
                content = f.read()
            self.text_area.delete("1.0", tk.END)
            self.text_area.insert("1.0", content)
            self.text_area.see("1.0")
        except Exception as e:
            messagebox.showerror("错误", f"无法读取文件：\n{e}")

    def on_closing(self):
        if self.typing_thread and self.typing_thread.is_alive():
            self.pause_event.set()
        self._unregister_hotkey()
        try:
            if self._drop_old_proc is not None:
                hwnd = HWND(self.window.winfo_id())
                user32.SetWindowLongPtrW(hwnd, GWL_WNDPROC, self._drop_old_proc)
        except Exception:
            pass
        self.window.destroy()

    def _reset_buttons(self):
        self.pause_frame.pack_forget()
        self.confirm_btn.config(text="▶  开始打字", bg=self.C["accent"], activebackground=self.C["accent"])
        self.confirm_btn.pack(fill=tk.X)
        self.file_btn.config(state="normal")
        self.text_area.config(state="normal", font=("Microsoft YaHei UI", 11), fg=self.C["text"])
        self.status_label.config(text="")

    def toggle_typing(self):
        if self.typing_thread and self.typing_thread.is_alive():
            if self.pause_event.is_set():
                self._resume_typing()
            else:
                self.pause_typing()
        else:
            self.start_typing()

    def start_typing(self):
        content = self.text_area.get("1.0", tk.END).strip()
        if not content:
            messagebox.showwarning("提示", "请输入或导入要打出的文本！")
            return

        self.typing_content = content
        self.typing_index = 0
        self.pause_event.clear()
        self.confirm_btn.config(text="⏸  暂停 · 空格", bg="#d4880f", activebackground="#d4880f")
        self.status_label.config(text="⏳ 倒计时中...", fg=self.C["yellow"])
        self.file_btn.config(state="disabled")
        self.text_area.config(state="normal")

        self.typing_thread = threading.Thread(target=self._do_countdown, daemon=True)
        self.typing_thread.start()

    def pause_typing(self):
        self.pause_event.set()
        self.confirm_btn.pack_forget()
        self.pause_frame.pack(fill=tk.X, pady=0)
        self.status_label.config(text="⏸ 已暂停 — 选择继续方式", fg=self.C["yellow"])
        self._bring_to_top()

    def _show_main_button(self):
        self.pause_frame.pack_forget()
        self.confirm_btn.pack(fill=tk.X)

    def _do_countdown(self):
        for i in range(3, 0, -1):
            if self.pause_event.is_set():
                self.window.after(0, self._restore_text_area)
                return
            self.window.after(0, lambda n=i: self._show_count_in_text(n))
            time.sleep(1)
        if self.pause_event.is_set():
            self.window.after(0, self._restore_text_area)
            return
        self.window.after(0, self._show_go_in_text)
        time.sleep(0.6)
        self.window.after(0, self._begin_typing)

    def _show_count_in_text(self, n):
        colors = ["#39ff14", "#00ffc8", "#ffc800", "#ff5050"]
        ci = min(3 - n, len(colors) - 1)
        self.text_area.config(font=("Microsoft YaHei UI", 44, "bold"))
        self.text_area.delete("1.0", tk.END)
        self.text_area.insert("1.0", f"\n   {n}")
        self.text_area.tag_configure("center", justify="center")
        self.text_area.tag_add("center", "1.0", tk.END)
        self.text_area.config(fg=colors[ci])

    def _show_go_in_text(self):
        self.text_area.delete("1.0", tk.END)
        self.text_area.insert("1.0", "\n  GO!")
        self.text_area.tag_configure("center", justify="center")
        self.text_area.tag_add("center", "1.0", tk.END)
        self.text_area.config(fg="#57ff14", font=("Microsoft YaHei UI", 44, "bold"))

    def _restore_text_area(self):
        self.text_area.config(font=("Microsoft YaHei UI", 11), fg=self.C["text"])
        self.text_area.delete("1.0", tk.END)
        self.text_area.config(state="disabled")

    def _begin_typing(self):
        self.text_area.config(state="normal")
        self.text_area.config(font=("Microsoft YaHei UI", 11), fg=self.C["text"])
        self.text_area.delete("1.0", tk.END)
        for tag in self.text_area.tag_names():
            self.text_area.tag_delete(tag)
        self.text_area.insert("1.0", self.typing_content)
        self.text_area.config(state="disabled")
        self.text_area.see("1.0")
        self.status_label.config(text="▶ 打字进行中...", fg=self.C["green"])
        self._send_to_bottom()

        if self.mode_is_english:
            switch_to_english()
            time.sleep(0.05)

        self.typing_thread = threading.Thread(target=self._run_typing, daemon=True)
        self.typing_thread.start()

    def _run_typing(self):
        if self.mode_is_english:
            user32.VkKeyScanW.argtypes = [ctypes.wintypes.WCHAR]
            user32.VkKeyScanW.restype = ctypes.wintypes.SHORT
            while self.typing_index < len(self.typing_content):
                if self.pause_event.is_set():
                    return
                ch = self.typing_content[self.typing_index]
                self.typing_index += 1
                if ch == '\n':
                    tap_key(VK_RETURN)
                elif ch == '\t':
                    tap_key(VK_TAB)
                else:
                    r = user32.VkKeyScanW(ctypes.wintypes.WCHAR(ch))
                    if r == -1:
                        continue
                    vk = r & 0xFF
                    ss = (r >> 8) & 0xFF
                    if ss & 1:
                        press_key(VK_SHIFT)
                        tap_key(vk)
                        release_key(VK_SHIFT)
                    else:
                        tap_key(vk)
                time.sleep(0.05)
        else:
            ch_buf = ""
            while self.typing_index < len(self.typing_content):
                if self.pause_event.is_set():
                    return
                ch = self.typing_content[self.typing_index]
                self.typing_index += 1
                if ch == '\n':
                    if ch_buf:
                        send_via_clipboard(ch_buf)
                        ch_buf = ""
                    tap_key(VK_RETURN)
                elif ch == '\t':
                    if ch_buf:
                        send_via_clipboard(ch_buf)
                        ch_buf = ""
                    tap_key(VK_TAB)
                elif is_ascii_printable(ch):
                    if ch_buf:
                        send_via_clipboard(ch_buf)
                        ch_buf = ""
                    user32.VkKeyScanW.argtypes = [ctypes.wintypes.WCHAR]
                    user32.VkKeyScanW.restype = ctypes.wintypes.SHORT
                    r = user32.VkKeyScanW(ctypes.wintypes.WCHAR(ch))
                    if r != -1:
                        vk = r & 0xFF
                        ss = (r >> 8) & 0xFF
                        if ss & 1:
                            press_key(VK_SHIFT)
                            tap_key(vk)
                            release_key(VK_SHIFT)
                        else:
                            tap_key(vk)
                else:
                    ch_buf += ch
                time.sleep(0.05)
            if ch_buf:
                send_via_clipboard(ch_buf)

        self.window.after(0, self.on_typing_finished)

    def on_typing_finished(self):
        self.pause_frame.pack_forget()
        self.confirm_btn.pack(fill=tk.X)
        self.confirm_btn.config(text="▶  开始打字", bg=self.C["accent"], activebackground=self.C["accent"])
        self.file_btn.config(state="normal")
        self.text_area.config(state="normal", font=("Microsoft YaHei UI", 11), fg=self.C["text"])
        self.text_area.delete("1.0", tk.END)
        self.text_area.insert("1.0", self.typing_content)
        self.text_area.see("1.0")
        self.status_label.config(text="✅ 打字已完成", fg=self.C["green"])
        self._bring_to_top()
        self.typing_thread = None


if __name__ == "__main__":
    TypeApp()
