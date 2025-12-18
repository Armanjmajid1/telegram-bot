import telebot
from telebot import types

TOKEN = "https://t.me/B7Rkurdbot?start=_tgr_HxS0FsxlZWVk"
bot = telebot.TeleBot(TOKEN, parse_mode="HTML")

# ================== DATABASE (RAM) ==================
GROUPS = {}        # chat_id : True / False
CHANNELS = {}      # chat_id : [@ch1, @ch2, ...]
JOIN_PHOTO = None  # file_id of join image

# ================== ADMIN CHECK ==================
def is_admin(message):
    try:
        m = bot.get_chat_member(message.chat.id, message.from_user.id)
        return m.status in ["administrator", "creator"]
    except:
        return False

# ================== /start (PRIVATE ONLY) ==================
@bot.message_handler(commands=["start"], chat_types=["private"])
def start(message):
    text = """
<b>👋 بخێرهاتی ❤️</b>

- ئەڤ بوتە بۆ زێدەكرنا ئەندامانە بۆ کەنال 🔐
- بوت ل گروپی خۆ admin بکە
- پاشان ل گروپی پەیامی <b>/on</b> بنێرە

<b>📌 ڕێنمایی:</b>
• /on → چالاككرنا بوت
• /off → راوستاندنا بوت
"""

    kb = types.InlineKeyboardMarkup()
    kb.add(
        types.InlineKeyboardButton(
            "➕ زێدەكرنا بوتی بۆ گروپ",
            url=f"https://t.me/{bot.get_me().username}?startgroup=true"
        )
    )
    bot.send_message(message.chat.id, text, reply_markup=kb)

# ================== ON ==================
@bot.message_handler(commands=["on"], chat_types=["group", "supergroup"])
def on_bot(message):
    if not is_admin(message):
        return

    GROUPS[message.chat.id] = True

    kb = types.InlineKeyboardMarkup()
    kb.add(
        types.InlineKeyboardButton("➕ زێدەكرنا کەنال", callback_data="add_channel"),
        types.InlineKeyboardButton("🖼 وێنەی Join", callback_data="set_photo")
    )

    bot.send_message(
        message.chat.id,
        "✅ بوت چالاك بو\n⬇️ دوگمە بكە بۆ زێدەكرنا کەنال یان وێنە",
        reply_markup=kb
    )

# ================== OFF ==================
@bot.message_handler(commands=["off"], chat_types=["group", "supergroup"])
def off_bot(message):
    if not is_admin(message):
        return
    GROUPS[message.chat.id] = False
    bot.send_message(message.chat.id, "⛔ بوت راوسترا")

# ================== CALLBACKS ==================
@bot.callback_query_handler(func=lambda c: c.data == "add_channel")
def ask_channel(call):
    if not is_admin(call.message):
        return
    msg = bot.send_message(call.message.chat.id, "📌 ناڤی کەنال بنڤیسە:\n@channel")
    bot.register_next_step_handler(msg, save_channel)

@bot.callback_query_handler(func=lambda c: c.data == "set_photo")
def ask_photo(call):
    if not is_admin(call.message):
        return
    bot.send_message(call.message.chat.id, "🖼 تکایە وێنە بنێرە (بۆ پەیامی Join)")

# ================== SAVE CHANNEL ==================
def save_channel(message):
    chat_id = message.chat.id
    ch = message.text.strip()

    if not ch.startswith("@"):
        bot.send_message(chat_id, "❌ ناڤی کەنال دەبێت بە @ دەستپێبکەت")
        return

    CHANNELS.setdefault(chat_id, []).append(ch)
    bot.send_message(chat_id, f"✅ کەنال زیادکرا: {ch}")

# ================== SAVE JOIN PHOTO ==================
@bot.message_handler(content_types=["photo"], chat_types=["group", "supergroup"])
def save_photo(message):
    global JOIN_PHOTO
    if not is_admin(message):
        return
    JOIN_PHOTO = message.photo[-1].file_id
    bot.send_message(message.chat.id, "✅ وێنەی Join هاتە تۆماركرن")

# ================== CHECK JOIN (DELETE MESSAGE) ==================
@bot.message_handler(func=lambda m: True, content_types=["text", "photo", "video", "document"])
def check_join(message):
    chat_id = message.chat.id

    if message.chat.type == "private":
        return
    if not GROUPS.get(chat_id):
        return

    channels = CHANNELS.get(chat_id, [])
    if not channels:
        return

    user_id = message.from_user.id

    for ch in channels:
        try:
            member = bot.get_chat_member(ch, user_id)
            if member.status in ["left", "kicked"]:
                raise Exception
        except:
            # DELETE USER MESSAGE
            try:
                bot.delete_message(chat_id, message.message_id)
            except:pass

            kb = types.InlineKeyboardMarkup()
            for c in channels:
                kb.add(
                    types.InlineKeyboardButton(
                        "📢 Join Channel",
                        url=f"https://t.me/{c.replace('@','')}"
                    )
                )

            text = f"""
❌ <b>{message.from_user.first_name}</b>

👇 سەرەتا ئەم کەنالانە Join بکە

• هەتا جوين نەکەيت
• هەر نامە دێ مسحکرن
• پاش جوين → پەیام كار دەكات

⚠️ بوت فریە
"""

            if JOIN_PHOTO:
                bot.send_photo(chat_id, JOIN_PHOTO, caption=text, reply_markup=kb)
            else:
                bot.send_message(chat_id, text, reply_markup=kb)
            return

# ================== RUN ==================
bot.infinity_polling()