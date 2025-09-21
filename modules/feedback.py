import sqlite3
from modules.utils import now_str

DB_PATH = "db/mebius.db"

# 📦 DB初期化
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

# 💾 手動フィードバック保存
def save_feedback(sender, receiver, feedback_text):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("INSERT INTO chat_feedback (sender, receiver, feedback, timestamp) VALUES (?, ?, ?, ?)",
              (sender, receiver, feedback_text, now_str()))
    conn.commit()
    conn.close()

# 📥 手動フィードバック取得（複数件）
def get_feedback(sender, receiver):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''SELECT feedback, timestamp FROM chat_feedback
                 WHERE sender=? AND receiver=?
                 ORDER BY timestamp DESC''', (sender, receiver))
    results = c.fetchall()
    conn.close()
    return results

# 🤖 自動フィードバック①：自分の発言割合
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

    if ratio > 0.7:
        comment = f"あなたの発言が多めでした（{int(ratio*100)}%）。問いかけが多かったかも？"
    elif ratio < 0.3:
        comment = f"相手の話をよく聞いていました（{int(ratio*100)}%）。沈黙の余白が活きていたかも。"
    else:
        comment = f"バランスの取れた会話でした（{int(ratio*100)}%）"

    return comment

# 🤖 自動フィードバック②：問いの頻度
def question_feedback(sender, receiver):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''SELECT sender, message FROM chat_messages
                 WHERE (sender=? AND receiver=?) OR (sender=? AND receiver=?)
                 ORDER BY timestamp''', (sender, receiver, receiver, sender))
    rows = c.fetchall()
    conn.close()

    if not rows:
        return "会話がまだありません"

    total = len(rows)
    question_count = sum(1 for s, m in rows if s == sender and "?" in m)
    ratio = question_count / total if total > 0 else 0

    if ratio > 0.5:
        comment = f"問いかけが多く、関係性を探る姿勢が見られました（{question_count}件）"
    elif ratio > 0.2:
        comment = f"問いが適度に含まれていて、会話に流れがありました（{question_count}件）"
    elif question_count == 0:
        comment = "問いかけはありませんでした。沈黙や受け止める時間が多かったかも"
    else:
        comment = f"問いは少なめでしたが、安心感を生む会話だったかもしれません（{question_count}件）"

    return comment