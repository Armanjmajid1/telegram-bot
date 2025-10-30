import telebot
from telebot import types
from datetime import datetime

# ==== توكن و یوزەرنەیمى بۆت ====
TOKEN = "8016109195:AAEu7Xr9nt9QIDAYJY4KObqmnuoKVpUXwm0"
OWNER = "@l7n07"

bot = telebot.TeleBot(TOKEN)

# ==== قفڵ و فەتح ====
locks = {}

def init_locks(chat_id):
    if chat_id not in locks:
        locks[chat_id] = {
            "links": False,
            "photos": False,
            "videos": False,
            "files": False,
            "gifs": False,
            "stickers": False
        }

# ==== start ====
@bot.message_handler(commands=["start"])
def start_message(message):
    if message.chat.type != "private":
        return

    text = f"""
👋 سڵاو {message.from_user.first_name}!
🤖 بۆتی پاراستنی گرووپ Police L7N بوتە.
👇 دوگمەی خوارەوە کرتە بکە:
"""

    keyboard = types.InlineKeyboardMarkup(row_width=1)
    keyboard.add(
        types.InlineKeyboardButton("➕ زیادکردنەوە بۆ گرووپ", url="https://t.me/policekurbot?startgroup=true"),
        types.InlineKeyboardButton("📞 چاتی تایبەتی", url=f"https://t.me/{OWNER.replace('@','')}")
    )
    bot.send_message(message.chat.id, text, reply_markup=keyboard)

# ==== فلتەر بۆ پاراستن پەیامەکان ====
@bot.message_handler(func=lambda m: m.chat.type in ["group", "supergroup"])
def protect_group(message):
    chat_id = message.chat.id
    init_locks(chat_id)

    # قفڵی لینک
    if locks[chat_id]["links"] and (("http" in message.text) or ("t.me" in message.text)):
        bot.delete_message(chat_id, message.message_id)
        return

    # قفڵی وێنە
    if locks[chat_id]["photos"] and message.content_type == "photo":
        bot.delete_message(chat_id, message.message_id)
        return

    # قفڵی ڤیدیۆ
    if locks[chat_id]["videos"] and message.content_type == "video":
        bot.delete_message(chat_id, message.message_id)
        return

    # قفڵی فایل
    if locks[chat_id]["files"] and message.content_type == "document":
        bot.delete_message(chat_id, message.message_id)
        return

    # قفڵی گیف
    if locks[chat_id]["gifs"] and message.content_type == "animation":
        bot.delete_message(chat_id, message.message_id)
        return

    # قفڵی ستیكر
    if locks[chat_id]["stickers"] and message.content_type == "sticker":
        bot.delete_message(chat_id, message.message_id)
        return

    # قفڵی مۆسیقا
    if "music" in locks[chat_id] and locks[chat_id]["music"] and message.audio:
        bot.delete_message(chat_id, message.message_id)
        return

    # قفڵی ڤۆیس
    if "voice" in locks[chat_id] and locks[chat_id]["voice"] and message.voice:
        bot.delete_message(chat_id, message.message_id)
        return
    for label, data in buttons:
        kb.add(types.InlineKeyboardButton(label, callback_data=data))

    bot.send_message(chat_id, text, reply_markup=kb)

# ==== قفڵ و فەتح بە دوگمە ====
@bot.callback_query_handler(func=lambda c: True)
def callback_handler(c):
    chat_id = c.message.chat.id
    init_locks(chat_id)

    if c.data.startswith("lock_"):
        key = c.data.split("_", 1)[1]
        locks[chat_id][key] = True
        bot.answer_callback_query(c.id, f"🔒 {key} قفڵ کرا")
    elif c.data.startswith("unlock_"):
        key = c.data.split("_", 1)[1]
        locks[chat_id][key] = False
        bot.answer_callback_query(c.id, f"🔓 {key} فەتح کرا")

# ==== بەخێرهاتنى ئەندامى نوێ ====
@bot.message_handler(content_types=["new_chat_members"])
def welcome_new_member(message):
    member = message.new_chat_members[0]
    name = member.first_name
    username = f"@{member.username}" if member.username else "بەکاربهێنەر نییە"
    date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    text = f"""
👋 بەخێر هاتیت {name}!
🆔 ID: {member.id}
🔗 یوزەر: {username}
📅 هاتیتە گرووپ: {date}
👮‍♂️ لەلایەن: {OWNER}
"""
    bot.send_photo(message.chat.id, "https://t.me/L7Nchannal", caption=text)

# ==== دەستپێك ====
print("🚀 PoliceBot دەستپێكرد...")
bot.infinity_polling()