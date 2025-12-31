import telebot
from telebot import types
import yt_dlp
import os

# ========= CONFIG =========
TOKEN = "8383702961:AAFgdNwax3qbH5eVnNczhllyjSEQ2KWzPjM"
CHANNEL_USERNAME = "@L7Nmovies"
OWNER_ID = 6583637773  # ID ـی خۆت

bot = telebot.TeleBot(TOKEN)
DOWNLOAD_DIR = "downloads"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

# ========= STATES =========
waiting_link = {}
custom_start_text = "👋 سلاف {name}!\nبەخێربێیت بۆ بۆتی دالنوت 🚀"

# ========= UTILS =========
def is_joined(user_id):
    try:
        m = bot.get_chat_member(CHANNEL_USERNAME, user_id)
        return m.status in ["member", "administrator", "creator"]
    except:
        return False

def join_lock(chat_id):
    kb = types.InlineKeyboardMarkup(row_width=1)
    kb.add(
        types.InlineKeyboardButton("📢 Join Channel", url=f"https://t.me/{CHANNEL_USERNAME.replace('@','')}"),
        types.InlineKeyboardButton("✅ Check Join", callback_data="check_join")
    )
    bot.send_message(
        chat_id,
        "🔒 بۆت قفلە!\n"
        "دفيت تو كه نالي جوين بكي 👇",
        reply_markup=kb
    )

# ========= START =========
@bot.message_handler(commands=["start"])
def start(msg):
    if not is_joined(msg.from_user.id):
        join_lock(msg.chat.id)
        return

    text = custom_start_text.format(name=msg.from_user.first_name)

    kb = types.InlineKeyboardMarkup(row_width=2)
    kb.add(
        types.InlineKeyboardButton("🎥 دالنوت ڤیدیۆ", callback_data="download"),
        types.InlineKeyboardButton("⚙️ Settings", callback_data="settings")
    )

    bot.send_message(msg.chat.id, text, reply_markup=kb)

# ========= CALLBACKS =========
@bot.callback_query_handler(func=lambda c: True)
def cb(call):
    uid = call.from_user.id
    cid = call.message.chat.id

    if not is_joined(uid):
        join_lock(cid)
        return

    # ---- CHECK JOIN ----
    if call.data == "check_join":
        if is_joined(uid):
            bot.answer_callback_query(call.id, "✅ جوين بو!")
            start(call.message)
        else:
            bot.answer_callback_query(call.id, "❌ هيشتا ته جوين نه كريه!", show_alert=True)

    # ---- DOWNLOAD ----
    elif call.data == "download":
        waiting_link[uid] = True
        kb = types.InlineKeyboardMarkup(row_width=1)
        kb.add(types.InlineKeyboardButton("⛔ داخستن", callback_data="close"))
        bot.send_message(
            cid,
            "🔗 نوكه لينكي فيديوي فريكه:\n"
            "YouTube / Instagram / TikTok / Telegram / public",
            reply_markup=kb
        )

    # ---- SETTINGS ----
    elif call.data == "settings":
        if uid != OWNER_ID:
            bot.answer_callback_query(call.id, "⛔ تني  Owner!", show_alert=True)
            return

        kb = types.InlineKeyboardMarkup(row_width=1)
        kb.add(
            types.InlineKeyboardButton("✏️ بدلكرنا پيامي Start", callback_data="edit_start"),
            types.InlineKeyboardButton("⛔ داخستن", callback_data="close")
        )
        bot.send_message(cid, "⚙️ Settings", reply_markup=kb)

    elif call.data == "edit_start":
        if uid == OWNER_ID:
            bot.send_message(cid, "✏️ پەیامی نوێ بنێرە:")
            waiting_link[uid] = "edit_start"

    elif call.data == "close":
        waiting_link.pop(uid, None)
        bot.delete_message(cid, call.message.message_id)

# ========= HANDLE TEXT =========
@bot.message_handler(func=lambda m: True)
def handle_text(msg):
    uid = msg.from_user.id
    cid = msg.chat.id

    if uid not in waiting_link:
        return

    # ---- EDIT START TEXT ----
    if waiting_link[uid] == "edit_start" and uid == OWNER_ID:
        global custom_start_text
        custom_start_text = msg.text
        waiting_link.pop(uid)
        bot.send_message(cid, "✅ پەیامی Start گۆڕا!")

    # ---- DOWNLOAD ----
    elif waiting_link[uid] is True and msg.text.startswith("http"):
        bot.send_message(cid, "⏳ نوكه دالنوت دبيت...")
        try:
            ydl_opts = {
                "format": "mp4",
                "outtmpl": f"{DOWNLOAD_DIR}/%(title).50s.%(ext)s",
                "quiet": True
            }
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(msg.text, download=True)
                file = ydl.prepare_filename(info)

            with open(file, "rb") as f:
                bot.send_video(cid, f)

            os.remove(file)
        except Exception as e:
            bot.send_message(cid, f"❌ خه له ته:\n{e}")

        waiting_link.pop(uid, None)

print("🤖 BOT READY")
bot.infinity_polling()