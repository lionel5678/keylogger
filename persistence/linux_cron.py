# ============================================================
#  persistence/linux_cron.py — Persistance Linux
#  Rôle : s'ajouter au crontab pour survivre au reboot
#  OS cible : Linux / macOS
# ============================================================

# ── CONCEPT : CRONTAB ────────────────────────────────────────
# cron est le scheduler de tâches sous Linux/macOS.
# Le crontab est le fichier qui liste les tâches planifiées
# de l'utilisateur courant.
#
# Format d'une ligne cron normale :
#   minute heure jour mois jour_semaine commande
#   *      *     *    *    *            → toutes les minutes
#
# Mot-clé spécial :
#   @reboot commande → s'exécute au démarrage du système
#
# On lit le crontab existant, on ajoute notre ligne @reboot,
# et on réécrit le tout via "crontab -" (stdin)

import subprocess
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from config import APP_NAME

MAIN_SCRIPT = os.path.normpath(os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "..", "main.py"
))
CRON_ENTRY = f"@reboot {sys.executable} {MAIN_SCRIPT}  # {APP_NAME}\n"


def install():
    """Ajoute l'entrée @reboot dans le crontab."""
    try:
        existing = _read_crontab()

        if MAIN_SCRIPT in existing:
            print("[Linux] Déjà installé dans crontab")
            return

        _write_crontab(existing + CRON_ENTRY)
        print("[Linux] ✅ Entrée crontab ajoutée")

    except Exception as e:
        print(f"[Linux] ❌ {e}")


def uninstall():
    """Supprime notre entrée du crontab."""
    try:
        existing = _read_crontab()
        # On filtre les lignes qui contiennent notre script
        filtered = "\n".join(
            line for line in existing.splitlines()
            if MAIN_SCRIPT not in line
        ) + "\n"
        _write_crontab(filtered)
        print("[Linux] ✅ Entrée crontab supprimée")
    except Exception as e:
        print(f"[Linux] ❌ {e}")


def is_installed():
    return MAIN_SCRIPT in _read_crontab()


def _read_crontab():
    """Lit le crontab courant. Retourne '' si vide."""
    result = subprocess.run(
        ["crontab", "-l"],
        capture_output=True, text=True
    )
    return result.stdout  # vide si pas de crontab


def _write_crontab(content):
    """Réécrit le crontab avec le contenu fourni."""
    subprocess.run(
        ["crontab", "-"],
        input=content, text=True, check=True
    )


if __name__ == "__main__":
    print(f"Script : {MAIN_SCRIPT}")
    print(f"Installé : {is_installed()}")
    install()