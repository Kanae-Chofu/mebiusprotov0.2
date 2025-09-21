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

def auto_feedback(sender, receiver):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''SELECT sender FROM chat_messages
                 WHERE (sender=? AND receiver=?) OR (sender=? AND receiver=?)''',
              (sender, receiver, receiver, sender))
    rows = c.fetchall()
    conn.close()

    if not rows:
        return "会話がまだありません"

    total = len(rows)
    sender_count = sum(1 for r in rows if r[0] == sender)
    ratio = sender_count / total

    # コメント生成（例）
    if ratio > 0.7:
        comment = f"あなたの発言が多めでした（{int(ratio*100)}%）。問いかけが多かったかも？"
    elif ratio < 0.3:
        comment = f"相手の話をよく聞いていました（{int(ratio*100)}%）。沈黙の余白が活きていたかも。"
    else:
        comment = f"バランスの取れた会話でした（{int(ratio*100)}%）"

    return comment