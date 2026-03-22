# ============================================================
#  core/screenshot.py — Capture d'écran automatique
#  Rôle : prendre une capture toutes les X secondes
#         et la sauvegarder dans storage/screenshots/
#  Dépendances : pip install pillow
# ============================================================

import threading
import time
import os
import sys
from datetime import datetime

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from config import SCREENSHOT_INTERVAL, SCREENSHOT_DIR


def take_screenshot():
    """
    Prend une capture d'écran et la sauvegarde en PNG.

    PIL/Pillow = bibliothèque Python pour manipuler les images.
    ImageGrab.grab() capture l'écran entier et retourne
    un objet Image que l'on sauvegarde ensuite.
    """
    try:
        from PIL import ImageGrab

        # Crée le dossier screenshots s'il n'existe pas
        os.makedirs(SCREENSHOT_DIR, exist_ok=True)

        # Nom de fichier horodaté pour ne jamais écraser
        filename  = datetime.now().strftime("%Y-%m-%d_%H-%M-%S") + ".png"
        filepath  = os.path.join(SCREENSHOT_DIR, filename)

        # Capture et sauvegarde
        screenshot = ImageGrab.grab()
        screenshot.save(filepath)

        print(f"[Screenshot] Sauvegardé : {filename}")
        return filepath

    except ImportError:
        print("[Screenshot] pip install pillow")
    except Exception as e:
        print(f"[Screenshot] Erreur : {e}")


class ScreenshotCapture:
    """
    Prend une capture toutes les SCREENSHOT_INTERVAL secondes
    dans un thread daemon.
    """
    def __init__(self):
        self.running = False

    def start(self):
        self.running = True
        print(f"[Screenshot] Démarré — capture toutes les {SCREENSHOT_INTERVAL}s")
        while self.running:
            take_screenshot()
            time.sleep(SCREENSHOT_INTERVAL)

    def stop(self):
        self.running = False


if __name__ == "__main__":
    print("[*] Test capture unique...")
    take_screenshot()