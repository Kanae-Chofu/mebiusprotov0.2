import sqlite3
from modules.utils import now_str

DB_PATH = "db/mebius.db"

def init_feedback_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS chat_feedback (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        sender TEXT,
        receiver TEXT,
        feedback TEXT,
        timestamp TEXT
    )''')
    conn.commit()
    conn.close()

def save_feedback(sender, receiver, feedback_text):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("INSERT INTO chat_feedback (sender, receiver, feedback, timestamp) VALUES (?, ?, ?, ?)",
              (sender, receiver, feedback_text, now_str()))
    conn.commit()
    conn.close()

def get_feedback(sender, receiver):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''SELECT feedback, timestamp FROM chat_feedback
                 WHERE sender=? AND receiver=?
                 ORDER BY timestamp DESC LIMIT 1''', (sender, receiver))
    result = c.fetchone()
    conn.close()
    return result if result else None