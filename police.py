import telebot
from telebot import types

# 🔑 توکەنی بۆتەکەت لێرە بنووسە
TOKEN = "8016109195:AAEu7Xr9nt9QIDAYJY4KObqmnuoKVpUXwm0"
bot = telebot.TeleBot(TOKEN)

# 🧱 پاراستنەکان
locks = {}

def init_locks(chat_id):
    if chat_id not in locks:
        locks[chat_id] = {
            "links": False,
            "photos": False,
            "videos": False,
            "files": False,
            "stickers": False,
            "gifs": False,
            "music": False,
            "voices": False,
            "all": False
        }

# 🧩 فانکشن بۆ دوگمەکانی پاراستن
def send_group_buttons(chat_id):
    kb = types.InlineKeyboardMarkup(row_width=2)
    kb.add(
        types.InlineKeyboardButton("🔒 قفل لینک", callback_data="lock_links"),
        types.InlineKeyboardButton("🔓 فەتح لینک", callback_data="unlock_links"),
        types.InlineKeyboardButton("🔒 قفل وێنە", callback_data="lock_photos"),
        types.InlineKeyboardButton("🔓 فەتح وێنە", callback_data="unlock_photos"),
        types.InlineKeyboardButton("🔒 قفل ڤیدیو", callback_data="lock_videos"),
        types.InlineKeyboardButton("🔓 فەتح ڤیدیو", callback_data="unlock_videos"),
        types.InlineKeyboardButton("🔒 قفل فایل", callback_data="lock_files"),
        types.InlineKeyboardButton("🔓 فەتح فایل", callback_data="unlock_files"),
        types.InlineKeyboardButton("🔒 قفل گیف", callback_data="lock_gifs"),
        types.InlineKeyboardButton("🔓 فەتح گیف", callback_data="unlock_gifs"),
        types.InlineKeyboardButton("🔒 قفل ستیکەر", callback_data="lock_stickers"),
        types.InlineKeyboardButton("🔓 فەتح ستیکەر", callback_data="unlock_stickers"),
        types.InlineKeyboardButton("🔒 قفل میوزیک 🎵", callback_data="lock_music"),
        types.InlineKeyboardButton("🔓 فەتح میوزیک 🎵", callback_data="unlock_music"),
        types.InlineKeyboardButton("🔒 قفل ڤۆیس 🔊", callback_data="lock_voices"),
        types.InlineKeyboardButton("🔓 فەتح ڤۆیس 🔊", callback_data="unlock_voices"),
        types.InlineKeyboardButton("👋 ناردنی پەیامی بەخێرهاتن", callback_data="send_welcome"),
        types.InlineKeyboardButton("🔒 قفل هەموو شت 🔐", callback_data="lock_all"),
        types.InlineKeyboardButton("🔓 فەتح هەموو شت 🔓", callback_data="unlock_all")
    )
    bot.send_message(chat_id, "🛡 بەشی پاراستن:\nدوگمەی خوازراوت هەڵبژێرە 👇", reply_markup=kb)

# ⚙️ بەکارهێنانی دوگمەکان (قفڵ، فەتح، بەخێرهاتن)
@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    chat_id = call.message.chat.id
    user_id = call.from_user.id
    init_locks(chat_id)

    try:
        member = bot.get_chat_member(chat_id, user_id)
        if member.status not in ["administrator", "creator"]:
            bot.answer_callback_query(call.id, "🚫 تەنها ئەدمین دەتوانێت ئەم دوگمەیە بەکاربێنێ!")
            return
    except:
        pass

    data = call.data

    # ✅ پەیامی بەخێرهاتن (هەمیار)
    if data == "send_welcome":
        try:
            chat_info = bot.get_chat(chat_id)
            group_name = chat_info.title

            # تێکستی بەخێرهاتن
            welcome_text = (
                f"👮‍♂️ بەخێربێیت بۆ گرووپی {group_name}!\n"
                "🎉 ئەم گرووپە بە پاراستنی Police L7N کار دەکات.\n\n"
                f"🆔 ID: `{user_id}`\n"
                f"👤 یوزەر: @{call.from_user.username if call.from_user.username else 'یوزەر نەهەیە'}"
            )

            # 🔗 دوگمەی ئەدمین بۆ لینک تایبەتی
            kb = types.InlineKeyboardMarkup()
            kb.add(types.InlineKeyboardButton("👮‍♂️ پەیوەندی بە خاوەنی بۆت", url="https://t.me/l7n07"))

            bot.send_message(chat_id, welcome_text, parse_mode="Markdown", reply_markup=kb)
            bot.answer_callback_query(call.id, "✅ پەیامی بەخێرهاتن نێردرا!")
        except Exception as e:
            bot.answer_callback_query(call.id, f"⚠️ هەڵەیەک ڕوویدا: {e}")

    elif data.startswith("lock_") or data.startswith("unlock_"):
        action, feature = data.split("_", 1)
        if feature == "all":
            for k in locks[chat_id]:
                locks[chat_id][k] = (action == "lock")
            bot.answer_callback_query(call.id, f"{'🔒' if action=='lock' else '🔓'} هەموو شت {'قفل' if action=='lock' else 'فەتح'} کرا")
        else:
            locks[chat_id][feature] = (action == "lock")
            bot.answer_callback_query(call.id, f"{'🔒' if action=='lock' else '🔓'} {feature} {'قفل' if action=='lock' else 'فەتح'} کرا")

# 🚫 پاراستنی گرووپ
@bot.message_handler(func=lambda m: True)
def group_filter(message):
    chat_id = message.chat.id
    init_locks(chat_id)

    if message.chat.type in ["group", "supergroup"] and message.text and "L7N" in message.text:
        send_group_buttons(chat_id)
        return

    try:
        if locks[chat_id]["links"] and message.text and ("http" in message.text or "t.me" in message.text):
            bot.delete_message(chat_id, message.message_id)
        if locks[chat_id]["photos"] and message.content_type == "photo":
            bot.delete_message(chat_id, message.message_id)
        if locks[chat_id]["videos"] and message.content_type == "video":
            bot.delete_message(chat_id, message.message_id)
        if locks[chat_id]["files"] and message.document:
            bot.delete_message(chat_id, message.message_id)
        if locks[chat_id]["stickers"] and message.content_type == "sticker":
            bot.delete_message(chat_id, message.message_id)
        if locks[chat_id]["gifs"] and message.content_type == "animation":
            bot.delete_message(chat_id, message.message_id)
        if locks[chat_id]["music"] and message.audio:
            bot.delete_message(chat_id, message.message_id)
        if locks[chat_id]["voices"] and message.voice:
            bot.delete_message(chat_id, message.message_id)
    except:
        pass

# 🏁 پەیامی Start لە پرایڤەت
@bot.message_handler(commands=["start"])
def start(message):
    if message.chat.type != "private":
        return

    text = (
        f"👋 سڵاو {message.from_user.first_name}!\n\n"
        "🚔 بەخێربێیت بۆ **Police L7N Bot**\n\n"
        "بەم بۆتە دەتوانی گرووپەکەت پارێزیت لە:\n"
        "🔗 لینک، 🖼 وێنە، 🎥 ڤیدیو، 🎵 میوزیک، 📄 فایل و هتد.\n\n"
        "👇 هەڵبژێرە چی دەخوازیت بکەیت:"
    )

    kb = types.InlineKeyboardMarkup(row_width=1)
    kb.add(
        types.InlineKeyboardButton("➕ زیادکردن بۆ گرووپ", url="https://t.me/policekurbot?startgroup=true"),
        types.InlineKeyboardButton("👤 جونا خاسی و نه‌ره‌ری", url="https://t.me/l7n07")
    )

    bot.send_message(message.chat.id, text, parse_mode="Markdown", reply_markup=kb)

print("🚓 Police L7N Bot — Welcome Ready ✅")
bot.infinity_polling(timeout=60, long_polling_timeout=60)