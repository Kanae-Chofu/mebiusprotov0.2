# modules/user.py
#共通ユーザー管理モジュール
import streamlit as st
import sqlite3
import bcrypt
from modules.utils import now_str

DB_PATH = "db/mebius.db"

# 🧱 DB初期化（usersテーブル）
def init_user_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users (
        username TEXT PRIMARY KEY,
        password TEXT,
        display_name TEXT,
        kari_id TEXT,
        registered_at TEXT
    )''')
    conn.commit()
    conn.close()

# 🆕 ユーザー登録
def register_user(username, password, display_name="", kari_id=""):
    username = username.strip()
    password = password.strip()
    if not username or not password:
        return "ユーザー名とパスワードを入力してください"

    hashed_pw = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    try:
        c.execute('''INSERT INTO users (username, password, display_name, kari_id, registered_at)
                     VALUES (?, ?, ?, ?, ?)''',
                  (username, hashed_pw, display_name, kari_id, now_str()))
        conn.commit()
        return "OK"
    except sqlite3.IntegrityError:
        return "このユーザー名は既に使われています"
    finally:
        conn.close()

# 🔐 ログイン
def login_user(username, password):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT password FROM users WHERE username=?", (username,))
    result = c.fetchone()
    conn.close()
    if result and bcrypt.checkpw(password.encode("utf-8"), result[0]):
        st.session_state.username = username
        return True
    return False

# 🧠 表示名取得（チャット用）
def get_display_name(username):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT display_name FROM users WHERE username=?", (username,))
    result = c.fetchone()
    conn.close()
    return result[0] if result and result[0] else username

# 🕶️ 仮ID取得（仮つながりスペース用）
def get_kari_id(username):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT kari_id FROM users WHERE username=?", (username,))
    result = c.fetchone()
    conn.close()
    return result[0] if result and result[0] else username

# 🧭 現在ログイン中のユーザー名
def get_current_user():
    return st.session_state.get("username", None)

# 🔓 ログアウト
def logout():
    st.session_state.username = None