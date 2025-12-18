import telebot
from telebot import types

TOKEN = "8502306914:AAGCbeQ85IaYirA8T9OuI3fqR6oKyZP8l6M"
bot = telebot.TeleBot(TOKEN, parse_mode="HTML")

# ===== DATABASE (RAM) =====
GROUPS = {}        # chat_id : True/False
CHANNELS = {}      # chat_id : [@ch1, @ch2]
JOIN_PHOTO = None  # file_id

# ===== ADMIN CHECK =====
def is_admin(chat_id, user_id):
    try:
        m = bot.get_chat_member(chat_id, user_id)
        return m.status in ["administrator", "creator"]
    except:
        return False

@bot.message_handler(commands=['start'])
def start(message):
    if message.chat.type != "private":
        return

    name = message.from_user.first_name

    text = f"""
👋 <b>{name}</b>

- بخيرهاتي  بۆ بۆتی زیده  كرنا انداما ل گروپي بۆ كه نالي ؛ 👥
- من ل كروپي خو بكه ادمين و كه نالي ؛ 👨‍✈️
- و پاشي پيامي <b>{{ on }}</b> فريكه گروپي
 
بوت هاتيه جيكرن راقي ؛ 
- نوكه تو دشئ  <b>[1]</b>    كه ناله كئ زيده بكه 🌸

- ئه گه ر ته فيت بوتي راوستينين پيامي <b>{{ off }}</b> فريكه كروپي ؛ ❎
"""

    markup = types.InlineKeyboardMarkup()
    markup.add(
        types.InlineKeyboardButton(
            "➕ زیادکردنی بۆت بۆ گروپ",
            url=f"https://t.me/{bot.get_me().username}?startgroup=true"
        )
    )

    bot.send_message(message.chat.id, text, reply_markup=markup)

bot.infinity_polling()

# =======================
# /on
# =======================
@bot.message_handler(commands=["on"])
def turn_on(message):
    if message.chat.type == "private":
        return
    if not is_admin(message.chat.id, message.from_user.id):
        return

    GROUPS[message.chat.id] = True

    kb = types.InlineKeyboardMarkup()
    kb.add(
        types.InlineKeyboardButton("➕ دانانی چەنال", callback_data="set_channel")
    )
    kb.add(
        types.InlineKeyboardButton("🖼 دانانی وێنەی Join", callback_data="set_photo")
    )

    bot.send_message(
        message.chat.id,
        "✅ بۆت چالاک بوو\nچەنالەکان دابنێ",
        reply_markup=kb
    )

# =======================
# /off
# =======================
@bot.message_handler(commands=["off"])
def turn_off(message):
    if message.chat.type == "private":
        return
    if not is_admin(message.chat.id, message.from_user.id):
        return

    GROUPS[message.chat.id] = False
    bot.send_message(message.chat.id, "⛔ بۆت ناچالاک بوو")

# =======================
# CALLBACKS
# =======================
@bot.callback_query_handler(func=lambda c: True)
def callbacks(call):
    if not is_admin(call.message.chat.id, call.from_user.id):
        return

    if call.data == "set_channel":
        bot.send_message(
            call.message.chat.id,
            "✍️ چەنالەکان بنووسە\nنمونە:\n@channel1 @channel2"
        )
        bot.register_next_step_handler(call.message, save_channels)

    elif call.data == "set_photo":
        bot.send_message(call.message.chat.id, "📸 وێنەی Join بنێرە")
        bot.register_next_step_handler(call.message, save_photo)

# =======================
# SAVE CHANNELS
# =======================
def save_channels(message):
    chs = message.text.split()
    CHANNELS[message.chat.id] = chs
    bot.send_message(message.chat.id, "✅ چەنالەکان هاتنە تۆمار")

# =======================
# SAVE JOIN PHOTO
# =======================
def save_photo(message):
    global JOIN_PHOTO
    if message.photo:
        JOIN_PHOTO = message.photo[-1].file_id
        bot.send_message(message.chat.id, "✅ وێنەی Join هاتە هەڵگرتن")

# ===============================
# CHECK JOIN (NO DELETE)
# ===============================
@bot.message_handler(func=lambda m: True, content_types=["text", "photo", "video"])
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

    # ⚠️ تەنها یەک جار ئاگاداری
    if WARNED.get((chat_id, user_id)):
        return

    for ch in channels:
        try:
            m = bot.get_chat_member(ch, user_id)
            if m.status in ["left", "kicked"]:
                raise Exception
        except:
            kb = types.InlineKeyboardMarkup()
            kb.add(
                types.InlineKeyboardButton(
                    "📢 Join Channel",
                    url=f"https://t.me/{ch.replace('@','')}"
                )
            )

            text = f"""❌ <b>{message.from_user.first_name}</b>

سەرەتا کەنال جوین بکە 👇
• بە ریز کەنالەکە جوین بکە
• دوای جوین پەیامەکەت کاردەکات
• ئەگەر جوین نەکەیت پەیام نایە

⚠️ بۆت فری دەکات
"""

            bot.send_message(chat_id, text, reply_markup=kb)
            WARNED[(chat_id, user_id)] = True
            return

# =======================
bot.infinity_polling()