import sqlite3
import re
from datetime import datetime
from modules.utils import now_str

DB_PATH = "db/mebius.db"

# 初期化
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

# 手動フィードバック保存・取得
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
                 ORDER BY timestamp DESC''', (sender, receiver))
    results = c.fetchall()
    conn.close()
    return results

# 会話取得（共通）
def get_chat(sender, receiver):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''SELECT sender, message, timestamp FROM chat_messages
                 WHERE (sender=? AND receiver=?) OR (sender=? AND receiver=?)
                 ORDER BY timestamp''', (sender, receiver, receiver, sender))
    rows = c.fetchall()
    conn.close()
    return rows

# 発言割合
def auto_feedback(sender, receiver):
    rows = get_chat(sender, receiver)
    if not rows:
        return "会話がまだありません"
    total = len(rows)
    sender_count = sum(1 for r in rows if r[0] == sender)
    ratio = sender_count / total
    if ratio > 0.7:
        return f"あなたの発言が多めでした（{int(ratio*100)}%）"
    elif ratio < 0.3:
        return f"相手の話をよく聞いていました（{int(ratio*100)}%）"
    else:
        return f"バランスの取れた会話でした（{int(ratio*100)}%）"

# 問いの頻度
def question_feedback(sender, receiver):
    rows = get_chat(sender, receiver)
    total = len(rows)
    question_count = sum(1 for s, m, _ in rows if s == sender and "?" in m)
    if question_count == 0:
        return "問いかけはありませんでした。沈黙や受け止める時間が多かったかも"
    elif question_count / total > 0.5:
        return f"問いかけが多く、関係性を探る姿勢が見られました（{question_count}件）"
    else:
        return f"問いが適度に含まれていて、会話に流れがありました（{question_count}件）"

# 沈黙の余白（平均秒数）
def silence_feedback(sender, receiver):
    rows = get_chat(sender, receiver)
    if len(rows) < 2:
        return "沈黙の分析には会話が少なすぎます"
    timestamps = [datetime.strptime(r[2], "%Y-%m-%d %H:%M:%S") for r in rows]
    gaps = [(timestamps[i] - timestamps[i-1]).total_seconds() for i in range(1, len(timestamps))]
    avg_gap = sum(gaps) / len(gaps)
    if avg_gap > 300:
        return f"沈黙の余白が長く、安心感を生む会話だったかもしれません（平均 {int(avg_gap)}秒）"
    elif avg_gap > 60:
        return f"適度な間があり、問いや受け止めが活きていたようです（平均 {int(avg_gap)}秒）"
    else:
        return f"テンポよく会話が進みました（平均 {int(avg_gap)}秒）"

# 感情語の使用率
def emotion_feedback(sender, receiver):
    emotion_words = ["嬉しい", "楽しい", "悲しい", "不安", "安心", "つらい", "好き", "嫌い"]
    rows = get_chat(sender, receiver)
    count = sum(1 for s, m, _ in rows if s == sender and any(word in m for word in emotion_words))
    if count == 0:
        return "感情表現は控えめでした。沈黙や問いが中心だったかも"
    elif count > 5:
        return f"感情を共有することで、関係性が深まっていたようです（{count}件）"
    else:
        return f"感情語が適度に使われていました（{count}件）"

# 応答率（簡易：相手の直後に返した回数）
def response_feedback(sender, receiver):
    rows = get_chat(sender, receiver)
    if len(rows) < 2:
        return "応答の分析には会話が少なすぎます"
    response_count = 0
    for i in range(1, len(rows)):
        prev_sender = rows[i-1][0]
        curr_sender = rows[i][0]
        if prev_sender != sender and curr_sender == sender:
            response_count += 1
    ratio = response_count / len(rows)
    if ratio > 0.4:
        return f"相手の言葉をよく受け止めていました（応答率 {int(ratio*100)}%）"
    else:
        return f"問いや沈黙が中心の会話だったかもしれません（応答率 {int(ratio*100)}%）"

# 会話の長さ
def length_feedback(sender, receiver):
    rows = get_chat(sender, receiver)
    if not rows:
        return "会話がまだありません"
    start = datetime.strptime(rows[0][2], "%Y-%m-%d %H:%M:%S")
    end = datetime.strptime(rows[-1][2], "%Y-%m-%d %H:%M:%S")
    duration = (end - start).total_seconds() / 60
    if len(rows) > 20 and duration > 30:
        return f"継続的なやりとりがあり、関係性が育っているようです（{len(rows)}件・{int(duration)}分）"
    else:
        return f"短めの会話でした（{len(rows)}件・{int(duration)}分）"