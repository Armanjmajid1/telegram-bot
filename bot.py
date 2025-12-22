import telebot
from telebot import types

TOKEN = "8502306914:AAGtTWs7lgrAVuwUKxClvyf6o38BSC9_nNg"
bot = telebot.TeleBot(TOKEN, parse_mode="HTML")

# ===== DATA =====
GROUP_ON = {}          # chat_id -> True/False
CHANNELS = {}          # chat_id -> {1: "@ch", 2: "@ch", 3: "@ch"}
JOIN_PHOTO = {}        # chat_id -> file_id

# ===== HELPERS =====
def is_admin(chat_id, user_id):
    try:
        member = bot.get_chat_member(chat_id, user_id)
        return member.status in ["administrator", "creator"]
    except:
        return False

def get_channels(chat_id):
    return CHANNELS.get(chat_id, {})

# ===== START (PRIVATE ONLY) =====
@bot.message_handler(commands=["start"], chat_types=["private"])
def start(message):
    user_name = message.from_user.first_name

    text = f"""
👋 <b>بەخێربێیت {user_name} ❤️</b>

━━━━━━━━━━━━━━
🤖 بۆتی Join Guard
━━━━━━━━━━━━━━

• بۆتی تایبەت بۆ پاراستنی گروپ 🔐
• ئەندام پێویستە کەناڵەکان Join بکات
• ئەگەر Join نەکات → پەیامەکە نایەت

━━━━━━━━━━━━━━
⚙️ چۆن کار بکات؟
━━━━━━━━━━━━━━

1️⃣ بۆت زیاد بکە بۆ گروپی خۆت  
2️⃣ بۆت بکە <b>Admin</b>  
3️⃣ لە گروپ بنووسە: <b>/on</b>  

━━━━━━━━━━━━━━
⛔ وەستاندن
━━━━━━━━━━━━━━

• لە گروپ بنووسە: <b>/off</b>

🌸 سوپاس بۆ بەکارهێنانی بۆتەکەمان
"""

    kb = types.InlineKeyboardMarkup()
    kb.add(
        types.InlineKeyboardButton(
            "➕ زیادکردنی بۆت بۆ گروپ",
            url=f"https://t.me/{bot.get_me().username}?startgroup=true"
        )
    )

    bot.send_message(
        message.chat.id,
        text,
        reply_markup=kb
    )
# ===== ON =====
@bot.message_handler(commands=["on"])
def on_cmd(message):
    if message.chat.type not in ["group", "supergroup"]:
        return
    if not is_admin(message.chat.id, message.from_user.id):
        return

    GROUP_ON[message.chat.id] = True
    CHANNELS.setdefault(message.chat.id, {})

    kb = types.InlineKeyboardMarkup(row_width=2)
    kb.add(
        types.InlineKeyboardButton("➕ کەناڵ 1", callback_data="add_1"),
        types.InlineKeyboardButton("❌ 1", callback_data="del_1"),
        types.InlineKeyboardButton("➕ کەناڵ 2", callback_data="add_2"),
        types.InlineKeyboardButton("❌ 2", callback_data="del_2"),
        types.InlineKeyboardButton("➕ کەناڵ 3", callback_data="add_3"),
        types.InlineKeyboardButton("❌ 3", callback_data="del_3"),
        types.InlineKeyboardButton("🖼 وێنە Join", callback_data="photo"),
        types.InlineKeyboardButton("🔒 داخستن", callback_data="close"),
    )

    bot.send_message(
        message.chat.id,
        "⚙️ <b>Settings Join Bot</b>",
        reply_markup=kb
    )

# ===== CALLBACKS =====
@bot.callback_query_handler(func=lambda c: True)
def callbacks(call):
    chat_id = call.message.chat.id
    uid = call.from_user.id

    if not is_admin(chat_id, uid):
        bot.answer_callback_query(call.id, "Admin تەنها ❌")
        return

    if call.data.startswith("add_"):
        num = int(call.data[-1])
        bot.send_message(chat_id, f"✍️ @کەناڵی {num} بنووسە")

        bot.register_next_step_handler(
            call.message,
            lambda m: CHANNELS[chat_id].update({num: m.text})
        )

    elif call.data.startswith("del_"):
        num = int(call.data[-1])
        CHANNELS.get(chat_id, {}).pop(num, None)
        bot.send_message(chat_id, f"🗑 کەناڵ {num} سڕایەوە")

    elif call.data == "photo":
        bot.send_message(chat_id, "🖼 وێنەی Join بنێرە")
        bot.register_next_step_handler(call.message, save_photo)

    elif call.data == "close":
        GROUP_ON[chat_id] = False
        bot.edit_message_text(
            "⛔ Join Bot داخرا",
            chat_id,
            call.message.message_id
        )

# ===== SAVE PHOTO =====
def save_photo(message):
    if not message.photo:
        return
    JOIN_PHOTO[message.chat.id] = message.photo[-1].file_id
    bot.send_message(message.chat.id, "✅ وێنە هاتە هەڵگرتن")

# ===== CHECK JOIN =====
@bot.message_handler(content_types=["text", "photo", "video", "document", "audio", "voice"])
def check_join(message):
    chat_id = message.chat.id

    # تەنها گروپ
    if message.chat.type == "private":
        return

    # ئەگەر بۆت چالاک نەبوو
    if not GROUP_ON.get(chat_id):
        return

    channels = CHANNELS.get(chat_id)
    if not channels:
        return

    user = message.from_user

    for ch in channels.values():
        try:
            member = bot.get_chat_member(ch, user.id)
            if member.status in ["left", "kicked"]:
                raise Exception
        except:
            # ❌ نامەی ئەندام بسڕەوە
            try:
                bot.delete_message(chat_id, message.message_id)
            except:
                pass

            # 🔘 دوگمەی Join
            kb = types.InlineKeyboardMarkup()
            for c in channels.values():
                kb.add(
                    types.InlineKeyboardButton(
                        "🔗 JOIN CHANNEL",
                        url=f"https://t.me/{c.replace('@','')}"
                    )
                )

            text = f"""
❌ <b>{user.first_name}</b>

⚠️ تکایە سەرەتا کەنال جوین بکە 👇

• ئەگەر جوین بکەیت → پەیامەکەت کار دەکات
• ئەگەر جوین نەکەیت → پەیامەکان دەسڕێنەوە
• بۆت فریە ⚡
"""

            # 🖼️ ئەگەر وێنەی Join هەیە
            if chat_id in JOIN_PHOTO:
                bot.send_photo(
                    chat_id,
                    JOIN_PHOTO[chat_id],
                    caption=text,
                    reply_markup=kb
                )
            else:
                bot.send_message(
                    chat_id,
                    text,
                    reply_markup=kb
                )
            return

# ===== RUN =====
bot.infinity_polling()