# Keylogger — Projet éducatif

> ⚠️ Usage strictement personnel sur ta propre machine / VM.
> Utiliser cet outil sur une machine tierce sans consentement est illégal.

## Structure

```
keylogger/
├── core/
│   ├── listener.py       # Hook clavier
│   ├── screenshot.py     # Capture d'écran
│   └── clipboard.py      # Surveillance presse-papier
├── storage/
│   └── logger.py         # Accès SQLite
├── exfil/
│   ├── mailer.py         # Envoi email (SMTP)
│   └── http_sender.py    # Envoi HTTP POST + serveur Flask
├── persistence/
│   ├── windows_startup.py
│   └── linux_cron.py
├── config.py             # Toute la config ici
└── main.py               # Point d'entrée
```

## Installation

```bash
pip install pynput pillow pyperclip requests flask pygetwindow
```

## Lancement

```bash
# Lancer le faux serveur email (MailHog)
./MailHog

# Dans un autre terminal — lancer le serveur HTTP récepteur
python exfil/http_sender.py server

# Lancer le keylogger
python main.py
```

## Config

Tout est dans `config.py` — intervalle d'envoi, email, URL serveur, etc.