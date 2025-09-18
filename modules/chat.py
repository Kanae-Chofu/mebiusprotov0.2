# modules/chat.py
import streamlit as st
import sqlite3
from modules.user import get_current_user, get_display_name
from modules.utils import now_str

DB_PATH = "db/mebius.db"

# 🧱 DB初期化（chat_messages）
def init_chat_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS chat_messages (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        sender TEXT,
        receiver TEXT,
        message TEXT,
        timestamp TEXT
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS friends (
        user TEXT,
        friend TEXT,
        UNIQUE(user, friend)
    )''')
    conn.commit()
    conn.close()

# 💬 メッセージ保存・取得
def save_message(sender, receiver, message):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("INSERT INTO chat_messages (sender, receiver, message, timestamp) VALUES (?, ?, ?, ?)",
              (sender, receiver, message, now_str()))
    conn.commit()
    conn.close()

def get_messages(user, partner):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''SELECT sender, message FROM chat_messages
                 WHERE (sender=? AND receiver=?) OR (sender=? AND receiver=?)
                 ORDER BY timestamp''', (user, partner, partner, user))
    messages = c.fetchall()
    conn.close()
    return messages

def get_friends(user):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT friend FROM friends WHERE user=?", (user,))
    friends = [row[0] for row in c.fetchall()]
    conn.close()
    return friends

# 🖥 UI表示
def render():
    init_chat_db()
    user = get_current_user()
    if not user:
        st.warning("ログインしてください（共通ID）")
        return

    st.subheader("💬 1対1チャット空間")
    st.write(f"あなたの表示名： `{get_display_name(user)}`")

    friends = get_friends(user)
    if not friends:
        st.info("まだ友達がいません。仮つながりスペースで申請してみましょう。")
        return

    partner = st.selectbox("チャット相手を選んでください", friends)
    if partner:
        st.session_state.partner = partner
        st.write(f"チャット相手： `{get_display_name(partner)}`")

        messages = get_messages(user, partner)
        for sender, msg in messages:
            align = "right" if sender == user else "left"
            bg = "#1F2F54" if align == "right" else "#426AB3"
            st.markdown(
                f"""<div style='text-align:{align}; margin:5px 0;'>
                <span style='background-color:{bg}; color:#FFFFFF; padding:8px 12px; border-radius:10px; display:inline-block; max-width:80%;'>
                {msg}
                </span></div>""", unsafe_allow_html=True
            )

        new_msg = st.chat_input("メッセージを入力")
        if new_msg:
            save_message(user, partner, new_msg)
            st.rerun()