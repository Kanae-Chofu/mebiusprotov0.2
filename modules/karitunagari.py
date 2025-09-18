# modules/karitunagari.py
import streamlit as st
import sqlite3
import random
from modules.user import get_current_user, get_kari_id
from modules.utils import now_str

DB_PATH = "db/mebius.db"

# 🧱 DB初期化（仮メッセージ）
def init_kari_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS kari_messages (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        sender TEXT,
        receiver TEXT,
        message TEXT,
        topic_theme TEXT,
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
def save_message(sender, receiver, message, theme=None):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("INSERT INTO kari_messages (sender, receiver, message, topic_theme, timestamp) VALUES (?, ?, ?, ?, ?)",
              (sender, receiver, message, theme, now_str()))
    conn.commit()
    conn.close()

def get_messages(user, partner):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''SELECT sender, message FROM kari_messages
                 WHERE (sender=? AND receiver=?) OR (sender=? AND receiver=?)
                 ORDER BY timestamp''', (user, partner, partner, user))
    messages = c.fetchall()
    conn.close()
    return messages

def get_shared_theme(user, partner):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''SELECT topic_theme FROM kari_messages
                 WHERE ((sender=? AND receiver=?) OR (sender=? AND receiver=?))
                 AND topic_theme IS NOT NULL
                 ORDER BY timestamp LIMIT 1''', (user, partner, partner, user))
    result = c.fetchone()
    conn.close()
    return result[0] if result else None

def add_friend(user, friend):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("INSERT OR IGNORE INTO friends (user, friend) VALUES (?, ?)", (user, friend))
    c.execute("INSERT OR IGNORE INTO friends (user, friend) VALUES (?, ?)", (friend, user))
    conn.commit()
    conn.close()

def get_friends(user):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT friend FROM friends WHERE user=?", (user,))
    friends = [row[0] for row in c.fetchall()]
    conn.close()
    return friends

# 🧠 話題カード
topics = {
    "猫": ["猫派？犬派？", "飼ってる猫の名前は？", "猫の仕草で好きなものは？"],
    "旅": ["最近行った場所は？", "旅先での思い出は？", "理想の旅って？"],
    "言葉": ["好きな言葉ある？", "座右の銘ってある？", "言葉に救われたことある？"]
}

# 🖥 UI表示
def render():
    init_kari_db()
    user = get_current_user()
    if not user:
        st.warning("ログインしてください（共通ID）")
        return

    kari_id = get_kari_id(user)
    st.subheader("🌌 仮つながりスペース")
    st.write(f"あなたの仮ID： `{kari_id}`")

    partner = st.text_input("話したい相手の仮IDを入力", key="partner_input")
    if partner:
        st.session_state.partner = partner
        st.write(f"相手： `{partner}`")

        shared_theme = get_shared_theme(kari_id, partner)

        if shared_theme:
            card_index = st.session_state.get("card_index", 0)
            st.markdown(f"この会話のテーマ：**{shared_theme}**")
            st.markdown(f"話題カード：**{topics[shared_theme][card_index]}**")
            if st.button("次の話題カード"):
                st.session_state.card_index = (card_index + 1) % len(topics[shared_theme])
                st.rerun()
        else:
            choices = random.sample(list(topics.keys()), 2)
            chosen = st.radio("話したいテーマを選んでください", choices)
            if st.button("このテーマで話す"):
                st.session_state.shared_theme = chosen
                st.session_state.card_index = 0
                st.rerun()

        messages = get_messages(kari_id, partner)
        for sender, msg in messages:
            align = "right" if sender == kari_id else "left"
            bg = "#1F2F54" if align == "right" else "#426AB3"
            st.markdown(
                f"""<div style='text-align:{align}; margin:5px 0;'>
                <span style='background-color:{bg}; color:#FFFFFF; padding:8px 12px; border-radius:10px; display:inline-block; max-width:80%;'>
                {msg}
                </span></div>""", unsafe_allow_html=True
            )

        new_msg = st.chat_input("メッセージを入力")
        if new_msg:
            theme = shared_theme or st.session_state.get("shared_theme")
            save_message(kari_id, partner, new_msg, theme)
            st.rerun()

        if len(messages) >= 6:
            st.success("この人と友達申請できます（3往復以上）")
            if st.button("友達になる"):
                add_friend(user, partner)
                st.success("友達に追加しました！チャット空間で表示名に切り替わります")

    st.divider()
    st.subheader("👥 あなたの友達一覧")
    friends = get_friends(user)
    if friends:
        for f in friends:
            st.markdown(f"- `{f}` さん（チャット空間で表示名に切り替わります）")
    else:
        st.info("まだ友達はいません")