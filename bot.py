import telebot
from telebot import types

TOKEN = "8502306914:AAGtTWs7lgrAVuwUKxClvyf6o38BSC9_nNg"
bot = telebot.TeleBot(TOKEN, parse_mode="HTML")

# ================= DATA =================
GROUP_ON = {}        # chat_id -> True/False
CHANNELS = {}        # chat_id -> {1:"@ch",2:"@ch",3:"@ch"}
JOIN_PHOTO = {}      # chat_id -> file_id

# ================= HELPERS =================
def is_admin(chat_id, user_id):
    try:
        m = bot.get_chat_member(chat_id, user_id)
        return m.status in ["administrator", "creator"]
    except:
        return False

# ================= START (PRIVATE) =================
@bot.message_handler(commands=["start"], chat_types=["private"])
def start(message):
    name = message.from_user.first_name

    text = f"""
👋 <b>بەخێربێیت {name} ❤️</b>

- بخێرهاتی بۆ بۆتی پاراستنی گروپ 🔐
- بۆت زیاد بکە بۆ گروپ
- بۆت بکە Admin
- لە گروپ بنووسە <b>/on</b>

✨ بۆت خۆکارە و پارێزراوە
"""

    kb = types.InlineKeyboardMarkup()
    kb.add(
        types.InlineKeyboardButton(
            "➕ زیادکردنی بۆت بۆ گروپ",
            url=f"https://t.me/{bot.get_me().username}?startgroup=true"
        )
    )

    bot.send_message(message.chat.id, text, reply_markup=kb)

# ================= ON =================
@bot.message_handler(commands=["on"], chat_types=["group","supergroup"])
def on_cmd(message):
    chat_id = message.chat.id
    if not is_admin(chat_id, message.from_user.id):
        return

    GROUP_ON[chat_id] = True
    CHANNELS.setdefault(chat_id, {})

    kb = types.InlineKeyboardMarkup(row_width=2)
    kb.add(
        types.InlineKeyboardButton("➕ کەناڵ 1", callback_data="add_1"),
        types.InlineKeyboardButton("❌ 1", callback_data="del_1"),
        types.InlineKeyboardButton("➕ کەناڵ 2", callback_data="add_2"),
        types.InlineKeyboardButton("❌ 2", callback_data="del_2"),
        types.InlineKeyboardButton("➕ کەناڵ 3", callback_data="add_3"),
        types.InlineKeyboardButton("❌ 3", callback_data="del_3"),
        types.InlineKeyboardButton("🖼 وێنەی Join", callback_data="photo"),
        types.InlineKeyboardButton("🔒 داخستن", callback_data="close")
    )

    bot.send_message(chat_id, "⚙️ <b>Settings Join Bot</b>", reply_markup=kb)

# ================= OFF =================
@bot.message_handler(commands=["off"], chat_types=["group","supergroup"])
def off_cmd(message):
    chat_id = message.chat.id
    if not is_admin(chat_id, message.from_user.id):
        return
    GROUP_ON[chat_id] = False
    bot.send_message(chat_id, "⛔ بۆت ناچالاک بوو")

# ================= CALLBACKS =================
@bot.callback_query_handler(func=lambda c: True)
def callbacks(call):
    chat_id = call.message.chat.id
    uid = call.from_user.id

    if not is_admin(chat_id, uid):
        bot.answer_callback_query(call.id, "❌ تەنها ئەدمین")
        return

    if call.data.startswith("add_"):
        num = int(call.data[-1])
        msg = bot.send_message(chat_id, f"✍️ @کەناڵی {num} بنووسە")
        bot.register_next_step_handler(msg, lambda m: save_channel(chat_id, num, m))

    elif call.data.startswith("del_"):
        num = int(call.data[-1])
        CHANNELS.get(chat_id, {}).pop(num, None)
        bot.send_message(chat_id, f"🗑 کەناڵ {num} سڕایەوە")

    elif call.data == "photo":
        msg = bot.send_message(chat_id, "🖼 وێنەی Join بنێرە")
        bot.register_next_step_handler(msg, save_photo)

    elif call.data == "close":
        GROUP_ON[chat_id] = False
        bot.edit_message_text("🔒 داخرا", chat_id, call.message.message_id)

def save_channel(chat_id, num, message):
    if not message.text.startswith("@"):
        bot.send_message(chat_id, "❌ ناوی کەناڵ بە @ دەست پێبکات")
        return
    CHANNELS[chat_id][num] = message.text
    bot.send_message(chat_id, f"✅ کەناڵ {num} زیادکرا")

def save_photo(message):
    JOIN_PHOTO[message.chat.id] = message.photo[-1].file_id
    bot.send_message(message.chat.id, "✅ وێنەی Join دانرا")

# ================= CHECK JOIN =================
@bot.message_handler(content_types=["text","photo","video","document"])
def check_join(message):
    chat_id = message.chat.id

    if message.chat.type == "private":
        return
    if not GROUP_ON.get(chat_id):
        return

    channels = CHANNELS.get(chat_id, {})
    if not channels:
        return

    user = message.from_user

    for ch in channels.values():
        try:
            m = bot.get_chat_member(ch, user.id)
            if m.status in ["left","kicked"]:
                raise Exception
        except:
            try:
                bot.delete_message(chat_id, message.message_id)
            except:
                pass

            kb = types.InlineKeyboardMarkup()
            for c in channels.values():
                kb.add(
                    types.InlineKeyboardButton(
                        "🔗 Join Channel",
                        url=f"https://t.me/{c.replace('@','')}"
                    )
                )

            text = f"""
❌ <b>{user.first_name}</b>

سەرەتا کەناڵ جوین بکە 👇
• دوای جوین نامەکانت دەرکەون
"""

            if chat_id in JOIN_PHOTO:
                bot.send_photo(chat_id, JOIN_PHOTO[chat_id], caption=text, reply_markup=kb)
            else:
                bot.send_message(chat_id, text, reply_markup=kb)
            break

# ================= RUN =================
bot.infinity_polling()