import telebot
from telebot import types
import time

TOKEN = "8386116524:AAH7UHj8vvsGziJrSHxqsTYcv7KUdumPNNk"  # 🔑 توکەنی خۆت لێرە بنووسە
bot = telebot.TeleBot(TOKEN)

# گۆڕاو بۆ چالاکی تاگکردن
mentioning_enabled = True

# ⚙️ چککردنی ئەدمین
def is_admin(chat_id, user_id):
    try:
        member = bot.get_chat_member(chat_id, user_id)
        return member.status in ["administrator", "creator"]
    except:
        return False

# 🚀 /start — تەنیا لە پرایڤەت
@bot.message_handler(commands=['start'])
def start_cmd(message):
    if message.chat.type != "private":
        bot.reply_to(message, "❌ ئەم فەرمانە تەنیا لە پرایڤەت کاردەکات.")
        return
    
    markup = types.InlineKeyboardMarkup(row_width=1)
    add_group = types.InlineKeyboardButton("➕ زیادکردنی بۆت بۆ گروپ", url=f"https://t.me/{bot.get_me().username}?startgroup=true")
    markup.add(add_group)

    bot.send_message(
        message.chat.id,
        "👋 سڵاو! 🌸\n\n"
        "ئەم بۆتە تایبەتە بۆ *تاگکردنی هەموو ئەندامەکانی گروپەکەت*.\n"
        "📌 بۆ بەکارهێنان:\n"
        "➕ بۆت زیاد بکە بۆ گروپەکەت\n"
        "🗣 بنوسە @all بۆ تاگکردنی ئەندامان.\n"
        "✋ بنوسە @off بۆ وەستاندنی تاگکردن.\n\n"
        "👇 کلیک بکە بۆ زیادکردن بۆ گروپ:",
        parse_mode="Markdown",
        reply_markup=markup
    )

# 📣 @all — تاگکردنی ئەدمینەکان
@bot.message_handler(func=lambda m: m.text and "@all" in m.text.lower())
def mention_all(message):
    global mentioning_enabled
    chat_id = message.chat.id
    user_id = message.from_user.id

    if not is_admin(chat_id, user_id):
        bot.reply_to(message, "🚫 تەنیا ئەدمین دەتوانێ @all بەکاربهێنێت.")
        return

    if not mentioning_enabled:
        bot.reply_to(message, "⛔ تاگکردن ناچالاکە! بۆ چالاککردن بنوسە /start لە پرایڤەت.")
        return

    bot.reply_to(message, "📢 دەستپێکرد بە تاگکردنی ئەندامەکان...")

    try:
        members = bot.get_chat_administrators(chat_id)
        names = []
        for member in members:
            if not member.user.is_bot:
                name = f"@{member.user.username}" if member.user.username else member.user.first_name
                names.append(name)

        if not names:
            bot.send_message(chat_id, "⚠️ هیچ ئەندامێک نەدۆزرایەوە.")
            return

        text = ""
        for i, name in enumerate(names, 1):
            text += name + " "
            if i % 4 == 0:
                bot.send_message(chat_id, text)
                text = ""
                time.sleep(1)
        if text:
            bot.send_message(chat_id, text)

        bot.send_message(chat_id, "✅ تاگکردن تەواو بوو.")
    except Exception as e:
        bot.send_message(chat_id, f"⚠️ هەڵەیەک ڕویدا:\n{e}")

# 📴 @off — وەستاندنی تاگکردن
@bot.message_handler(func=lambda m: m.text and "@off" in m.text.lower())
def disable_mentions(message):
    global mentioning_enabled
    chat_id = message.chat.id
    user_id = message.from_user.id

    if not is_admin(chat_id, user_id):
        bot.reply_to(message, "🚫 تەنیا ئەدمین دەتوانێ @off بەکاربهێنێت.")
        return

    mentioning_enabled = False
    bot.send_message(chat_id, "🛑 تاگکردن وەستێت.")

print("🤖 Bot چالاکە و ئامادەیە 🔥")
bot.infinity_polling()