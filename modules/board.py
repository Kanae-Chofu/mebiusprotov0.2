# modules/board.py
import streamlit as st
import sqlite3
from modules.utils import now_str, sanitize_message
from modules.user import get_current_user

DB_PATH = "db/mebius.db"

# 🧱 DB初期化（スレッド・メッセージ）
def init_board_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS threads (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT,
        created_at TEXT
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS board_messages (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT,
        message TEXT,
        timestamp TEXT,
        thread_id INTEGER
    )''')
    conn.commit()
    conn.close()

# 📥 スレッド・メッセージ処理
def create_thread(title):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("INSERT INTO threads (title, created_at) VALUES (?, ?)", (title, now_str()))
    conn.commit()
    conn.close()

def load_threads():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT id, title, created_at FROM threads ORDER BY id DESC")
    threads = c.fetchall()
    conn.close()
    return threads

def save_message(username, message, thread_id):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("INSERT INTO board_messages (username, message, timestamp, thread_id) VALUES (?, ?, ?, ?)",
              (username, message, now_str(), thread_id))
    conn.commit()
    conn.close()

def load_messages(thread_id):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT username, message, timestamp FROM board_messages WHERE thread_id=? ORDER BY id DESC", (thread_id,))
    messages = c.fetchall()
    conn.close()
    return messages

# 🖥 UI表示
def render():
    init_board_db()
    user = get_current_user()
    if not user:
        st.warning("ログインしてください（共通ID）")
        return

    st.subheader("🧵 掲示板スレッド一覧")
    threads = load_threads()

    # スレッド作成フォーム
    with st.form(key="thread_form", clear_on_submit=True):
        new_title = st.text_input("新しいスレッド名（64文字まで）", max_chars=64)
        submitted = st.form_submit_button("スレッド作成")
        if submitted:
            title = sanitize_message(new_title, 64)
            if title:
                create_thread(title)
                st.success("スレッドを作成しました")
                st.rerun()
            else:
                st.warning("スレッド名を入力してください")

    st.markdown("---")
    for tid, title, created in threads:
        if st.button(f"{title}（{created}）", key=f"thread_{tid}"):
            st.session_state.thread_id = tid
            st.rerun()

    # スレッド選択後の表示
    if "thread_id" in st.session_state:
        st.subheader(f"🗨️ スレッド: {st.session_state.thread_id}")
        if st.button("← スレ一覧に戻る"):
            del st.session_state.thread_id
            st.rerun()

        messages = load_messages(st.session_state.thread_id)
        for username, msg, ts in messages:
            st.write(f"[{ts}] **{username}**: {msg}")

        # メッセージ送信フォーム（エンターキー対応）
        with st.form(key="board_form", clear_on_submit=True):
            new_msg = st.text_input("メッセージ（150文字まで）", max_chars=150)
            submitted = st.form_submit_button("送信")
            if submitted:
                msg = sanitize_message(new_msg, 150)
                if msg:
                    save_message(user, msg, st.session_state.thread_id)
                    st.rerun()
                else:
                    st.warning("メッセージを入力してください")