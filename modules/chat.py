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