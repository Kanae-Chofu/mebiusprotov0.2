# main.py
import streamlit as st
from modules import board, karitunagari, chat

# 🌙 ダークモードCSS（共通）
st.markdown("""
<style>
body, .stApp { background-color: #000000; color: #FFFFFF; }
div[data-testid="stHeader"] { background-color: #000000; }
div[data-testid="stToolbar"] { display: none; }
input, textarea { background-color: #1F2F54 !important; color:#FFFFFF !important; }
button { background-color: #426AB3 !important; color:#FFFFFF !important; border: none !important; }
</style>
""", unsafe_allow_html=True)

# 🧭 タイトルと空間選択
st.title("めびうす redesign")
st.caption("問いと沈黙から始まる、関係性の設計空間")

space = st.radio("空間を選んでください", ["掲示板", "仮つながりスペース", "1対1チャット"], horizontal=True)

from modules.user import login_user, register_user, get_current_user

if get_current_user() is None:
    st.subheader("🔐 ログイン")
    login_user = st.text_input("ユーザー名", key="login_username")
    login_pass = st.text_input("パスワード", type="password", key="login_password")
    if st.button("ログイン"):
        if login_user(username, password):
            st.success("ログインしました")
            st.rerun()
        else:
            st.error("ログイン失敗")

    st.subheader("🆕 新規登録")
    new_user = st.text_input("ユーザー名", key="register_username")
    new_pass = st.text_input("パスワード", type="password", key="register_password")

    if st.button("登録"):
        result = register_user(new_user, new_pass)
        if result == "OK":
            st.success("登録完了！ログインしてください")
        else:
            st.error(result)
    st.stop()

# 🚪空間ごとのルーティング
if space == "掲示板":
    board.render()

elif space == "仮つながりスペース":
    karitunagari.render()

elif space == "1対1チャット":
    chat.render()