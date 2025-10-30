import telebot
from telebot import types
from datetime import datetime

# ==== توكن و یوزەرنەیمى بۆت ====
TOKEN = "8016109195:AAEu7Xr9nt9QIDAYJY4KObqmnuoKVpUXwm0"
OWNER = "@L7n07"

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
👋 سلاف' {message.from_user.first_name}!
🤖 بۆتئ پاراستنا گروپي  Police L7N بوتە.
👇 دوو دوگمه ل خارئ نه بو زيده كرنا بوتي بو گروپي دوگما دي بو هه ر اريشه كي نامه كي فريكه:
"""

    keyboard = types.InlineKeyboardMarkup(row_width=1)
    keyboard.add(
        types.InlineKeyboardButton("➕ بوتي ل گروپئ خو زيده بكه", url="https://t.me/policekurbot?startgroup=true"),
        types.InlineKeyboardButton("📞 𝐎𝐰𝐧𝐞𝐫👑 ", url=f"https://t.me/{OWNER.replace('@','')}")
    )
    bot.send_message(message.chat.id, text, reply_markup=keyboard)

# ==== فلتەر بۆ پاراستن پەیامەکان ====
@bot.message_handler(func=lambda m: m.chat.type in ["group", "supergroup"])
def protect_group(message):
    chat_id = message.chat.id
    init_locks(chat_id)

    # گرتنا لينكا
    if locks[chat_id]["links"] and (("http" in message.text) or ("t.me" in message.text)):
        bot.delete_message(chat_id, message.message_id)
        return

    # گرتنا وئنا
    if locks[chat_id]["photos"] and message.content_type == "photo":
        bot.delete_message(chat_id, message.message_id)
        return

    # گرتنا فيديويا
    if locks[chat_id]["videos"] and message.content_type == "video":
        bot.delete_message(chat_id, message.message_id)
        return

    # گرتنا فايلا
    if locks[chat_id]["files"] and message.content_type == "document":
        bot.delete_message(chat_id, message.message_id)
        return

    # گرتنا گيفتا
    if locks[chat_id]["gifs"] and message.content_type == "animation":
        bot.delete_message(chat_id, message.message_id)
        return

    # گرتنا ستيكه را
    if locks[chat_id]["stickers"] and message.content_type == "sticker":
        bot.delete_message(chat_id, message.message_id)
        return

    # گرتنا سترانا
    if "music" in locks[chat_id] and locks[chat_id]["music"] and message.audio:
        bot.delete_message(chat_id, message.message_id)
        return

    # قفڵی ستیكر
    if locks[chat_id]["stickers"] and message.content_type == "sticker":
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
        bot.answer_callback_query(c.id, f"🔒 {key} گرت")
    elif c.data.startswith("unlock_"):
        key = c.data.split("_", 1)[1]
        locks[chat_id][key] = False
        bot.answer_callback_query(c.id, f"🔓 {key} فه كر")

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