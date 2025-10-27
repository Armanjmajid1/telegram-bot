get_chat_member(chat_id, user_id).user.username or bot.get_chat_member(chat_id, user_id).user.first_name}, {reason_text}")
    except:
        # fallback
        bot.send_message(chat_id, "⚠️ پەیامەکە سڕدرا (هۆک: {})".format(reason_text))

def mute_user(chat_id, user_id, seconds):
    try:
        until = int(time.time()) + seconds
        bot.restrict_chat_member(chat_id, user_id, can_send_messages=False, until_date=until)
        bot.send_message(chat_id, f"🔇 بەکارهێنەرەکە مۆد کرا بۆ {seconds} چرکە.")
    except Exception as e:
        print("mute err:", e)

# ---------- flood tracking ----------
def check_flood(chat_id, user_id):
    max_msgs, window = flood_limits[chat_id]
    dq = user_msgs[chat_id][user_id]
    now = time.time()
    dq.append(now)
    # pop old
    while dq and dq[0] < now - window:
        dq.popleft()
    if len(dq) > max_msgs:
        return True
    return False

# ---------- message handler: main protection ----------
@bot.message_handler(content_types=['text','photo','video','voice','document','sticker','animation'])
def protect(message):
    chat_id = message.chat.id
    if message.chat.type not in ["group","supergroup"]:
        return

    init_locks(chat_id)
    user_id = message.from_user.id

    # admins exempt
    if is_admin(chat_id, user_id):
        return

    text = (message.caption or message.text or "").strip()

    # 1) links
    if locks[chat_id].get("links") and re.search(r"(https?://|t\.me/|www\.)", text, re.I):
        delete_and_warn(chat_id, user_id, message.message_id, "ناتوانیت لینک بنێریت — تەنها ئەدمین دەتوانێ.")
        return

    # 2) photos
    if locks[chat_id].get("photos") and message.photo:
        delete_and_warn(chat_id, user_id, message.message_id, "ناتوانیت وێنە بنێریت.")
        return

    # 3) git
    if locks[chat_id].get("git") and re.search(r"(github\.com|gitlab\.com)", text, re.I):
        delete_and_warn(chat_id, user_id, message.message_id, "ناتوانیت لینکی گیت بنێریت.")
        return

    # 4) sex words
    if locks[chat_id].get("sex") and re.search(r"\b(sex|xxx|nude|裸)\b", text, re.I):
        delete_and_warn(chat_id, user_id, message.message_id, "کەرەستە و مەواد نایاسا قەدەغە کراون.")
        return

    # 5) videos
    if locks[chat_id].get("videos") and message.video:
        delete_and_warn(chat_id, user_id, message.message_id, "ناتوانیت ڤیدیۆ بنێریت.")
        return

    # 6) voice
    if locks[chat_id].get("voice") and (message.voice or message.audio):
        delete_and_warn(chat_id, user_id, message.message_id, "ناتوانیت ڤۆیس یان ڕێکەوتە بنێریت.")
        return

    # 7) files (document)
    if locks[chat_id].get("files") and message.document:
        delete_and_warn(chat_id, user_id, message.message_id, "ناتوانیت فایل بنێریت.")
        return

    # 8) stickers
    if locks[chat_id].get("stickers") and message.sticker:
        delete_and_warn(chat_id, user_id, message.message_id, "ناتوانیت استیکەر بنێریت.")
        return

    # 9) gifs
    if locks[chat_id].get("gifs") and message.animation:
        delete_and_warn(chat_id, user_id, message.message_id, "ناتوانیت گیف بنێریت.")
        return

    # 10) media (any)
    if locks[chat_id].get("media") and (message.photo or message.video or message.document):
        delete_and_warn(chat_id, user_id, message.message_id, "ناتوانیت میدیا بنێریت.")
        return

    # 11) exefiles (.apk .exe .zip .rar .7z)
    if locks[chat_id].get("exefiles") and message.document:
        fname = (message.document.file_name or "").lower()
        if any(fname.endswith(ext) for ext in [".apk",".exe",".zip",".rar",".7z"]):
            delete_and_warn(chat_id, user_id, message.message_id, "بارکردنی ئەم جۆر فایڵان قەدەغەیە.")
            return

    # 12) spam length
    if text and len(text) >= spam_length_threshold[chat_id]:
        delete_and_warn(chat_id, user_id, message.message_id, "پەیامە درێژەکان وەک سپام پێناسە دەکرێن — تکایە خێرا بنووسە.")
        return

    # 13) flood (rate limit)
    if check_flood(chat_id, user_id):
        mute_time = flood_mute_seconds[chat_id]mute_user(chat_id, user_id, mute_time)
        delete_and_warn(chat_id, user_id, message.message_id, f"تۆ پەیام زۆر نارد — مۆد کراوەتەوە بۆ {mute_time} چرکە.")
        # clear deque to avoid repeated mutes
        user_msgs[chat_id][user_id].clear()
        return

# ---------- optional admin commands to configure ----------
@bot.message_handler(commands=['set_spam_len'])
def cmd_set_spam(message):
    if not is_admin(message.chat.id, message.from_user.id):
        return
    parts = message.text.split()
    if len(parts) >= 2 and parts[1].isdigit():
        spam_length_threshold[message.chat.id] = int(parts[1])
        bot.reply_to(message, f"✅ Threshold set to {parts[1]} chars.")
    else:
        bot.reply_to(message, "Usage: /set_spam_len 800")

@bot.message_handler(commands=['set_flood'])
def cmd_set_flood(message):
    if not is_admin(message.chat.id, message.from_user.id):
        return
    parts = message.text.split()
    if len(parts) >= 3 and parts[1].isdigit() and parts[2].isdigit():
        flood_limits[message.chat.id] = (int(parts[1]), int(parts[2]))
        bot.reply_to(message, f"✅ Flood set to {parts[1]} msgs / {parts[2]} sec")
    else:
        bot.reply_to(message, "Usage: /set_flood <max_msgs> <seconds>")

@bot.message_handler(commands=['set_mute'])
def cmd_set_mute(message):
    if not is_admin(message.chat.id, message.from_user.id):
        return
    parts = message.text.split()
    if len(parts) >= 2 and parts[1].isdigit():
        flood_mute_seconds[message.chat.id] = int(parts[1])
        bot.reply_to(message, f"✅ Mute time set to {parts[1]} seconds")
    else:
        bot.reply_to(message, "Usage: /set_mute <seconds>")

# ---------- start ----------
print("🚔 PolîsBot running with extended protections...")
bot.infinity_polling()