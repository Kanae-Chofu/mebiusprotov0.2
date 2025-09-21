import streamlit as st
import sqlite3
from modules.user import get_current_user, get_display_name
from modules.utils import now_str
from modules.feedback import (
    init_feedback_db,
    save_feedback,
    get_feedback,
    auto_feedback,
    question_feedback
)

DB_PATH = "db/mebius.db"

# DB初期化
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

# メッセージ保存・取得
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

# 友達管理
def get_friends(user):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT friend FROM friends WHERE user=?", (user,))
    friends = [row[0] for row in c.fetchall()]
    conn.close()
    return friends

def add_friend(user, friend):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("INSERT OR IGNORE INTO friends (user, friend) VALUES (?, ?)", (user, friend))
    conn.commit()
    conn.close()

# UI表示
def render():
    init_chat_db()
    init_feedback_db()

    user = get_current_user()
    if not user:
        st.warning("ログインしてください（共通ID）")
        return

    st.write(f"あなたの表示名： `{get_display_name(user)}`")

    # 友達追加
    st.markdown("### 友達追加")
    new_friend = st.text_input("追加したいユーザー名", key="add_friend_input")
    if st.button("追加"):
        if new_friend and new_friend != user:
            add_friend(user, new_friend)
            st.success(f"{new_friend} を追加しました")
            st.rerun()
        else:
            st.error("自分自身は追加できません")

    # チャット相手選択
    friends = get_friends(user)
    if not friends:
        st.write("まだ友達がいません。追加してください。")
        return

    partner = st.selectbox("チャット相手を選択", friends)
    if partner:
        st.write(f"チャット相手： `{get_display_name(partner)}`")

        # メッセージ表示
        messages = get_messages(user, partner)
        for sender, msg in messages:
            prefix = "あなた：" if sender == user else f"{get_display_name(sender)}："
            st.write(f"{prefix} {msg}")

        # メッセージ入力
        new_msg = st.chat_input("メッセージを入力")
        if new_msg:
            save_message(user, partner, new_msg)
            st.rerun()

        # AIフィードバック（シンプル表示）
        st.markdown("### AIフィードバック")
        st.write("・発言割合：" + auto_feedback(user, partner))
        st.write("・問いの頻度：" + question_feedback(user, partner))

        # 手動フィードバック
        st.markdown("### あなたのフィードバック")
        feedback_list = get_feedback(user, partner)
        if feedback_list:
            for fb, ts in feedback_list:
                st.write(f"- {fb}（{ts}）")
        else:
            st.write("まだフィードバックはありません。")

        feedback_text = st.text_input("フィードバックを入力", key="feedback_input")
        if st.button("送信"):
            if feedback_text:
                save_feedback(user, partner, feedback_text)
                st.success("フィードバックを保存しました")
                st.rerun()
            else:
                st.warning("フィードバックを入力してください")