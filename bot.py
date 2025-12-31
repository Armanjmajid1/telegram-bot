import telebot
from telebot import types
import yt_dlp
import os

# ================= CONFIG =================
TOKEN = "8383702961:AAFgdNwax3qbH5eVnNczhllyjSEQ2KWzPjM"
OWNER_ID = 6583637773
CHANNEL_USERNAME = "@L7nmovies"
OWNER_LINK = "https://t.me/L7N07"

bot = telebot.TeleBot(TOKEN, threaded=True, num_threads=8)
DOWNLOAD_DIR = "downloads"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

# ================= UI (CUSTOMIZE EVERYTHING) =================
ui = {
    # TEXTS
    "start": "👋 سلاف {name}!\n🚀 بەخێربێیت بۆ بۆتی دالنوت",
    "join": "🔒 تکایە سەرەتا کەناڵ join بکە",
    "ask_link": "🔗 لینکی ڤیدیۆ بنێرە",
    "downloading": "⏳ دالنوت دەست پێکرد...",
    "done": "✅ ڤیدیۆ دالنوت بوو!",
    "error": "❌ دالنوت سەرکەوتوو نەبوو",

    # BUTTONS
    "btn_download": "🎥 دالنوت ڤیدیۆ",
    "btn_again": "🔁 دالنوت ڤیدیۆی دیکە",
    "btn_close": "⛔ داخستن",
    "btn_settings": "⚙️ Settings",
    "btn_owner": "📩 پەیوەندی بە Owner",
    "btn_join": "📢 Join Channel"
}

# ================= STATES =================
wait_link = {}
wait_edit = {}
wait_photo = {}
wait_channel = {}
start_photo = None

# ================= UTILS =================
def is_joined(user_id):
    try:
        m = bot.get_chat_member(CHANNEL_USERNAME, user_id)
        return m.status in ["member", "administrator", "creator"]
    except:
        return False

def base_kb(extra=None):
    kb = types.InlineKeyboardMarkup(row_width=1)
    if extra:
        for b in extra:
            kb.add(b)
    kb.add(types.InlineKeyboardButton(ui["btn_owner"], url=OWNER_LINK))
    return kb

def join_lock(chat_id):
    kb = base_kb([
        types.InlineKeyboardButton(
            ui["btn_join"],
            url=f"https://t.me/{CHANNEL_USERNAME.replace('@','')}"
        ),
        types.InlineKeyboardButton("✅ Check", callback_data="check_join")
    ])
    bot.send_message(chat_id, ui["join"], reply_markup=kb)

def again_kb():
    return base_kb([
        types.InlineKeyboardButton(ui["btn_again"], callback_data="download"),
        types.InlineKeyboardButton(ui["btn_close"], callback_data="close")
    ])

# ================= NOTIFY OWNER ON START =================
def notify_owner_start(user):
    text = (
        "🚀 <b>Start نوێ</b>\n\n"
        f"👤 ناو: {user.first_name}\n"
        f"🆔 ID: <code>{user.id}</code>\n"
        f"🔗 Username: @{user.username}" if user.username else
        f"🚀 <b>Start نوێ</b>\n\n"
        f"👤 ناو: {user.first_name}\n"
        f"🆔 ID: <code>{user.id}</code>\n"
        f"🔗 Username: ❌"
    )

    try:
        photos = bot.get_user_profile_photos(user.id, limit=1)
        if photos.total_count > 0:
            file_id = photos.photos[0][-1].file_id
            bot.send_photo(
                OWNER_ID,
                file_id,
                caption=text,
                parse_mode="HTML"
            )
        else:
            bot.send_message(OWNER_ID, text, parse_mode="HTML")
    except:
        bot.send_message(OWNER_ID, text, parse_mode="HTML")

# ================= /ID =================
@bot.message_handler(commands=["id"])
def myid(msg):
    bot.send_message(msg.chat.id, f"🆔 {msg.from_user.id}")

# ================= START =================
@bot.message_handler(commands=["start"])
def start(msg):
    # 🔔 notify owner
    notify_owner_start(msg.from_user)

    if not is_joined(msg.from_user.id):
        join_lock(msg.chat.id)
        return

    text = ui["start"].format(name=msg.from_user.first_name)
    kb = base_kb([
        types.InlineKeyboardButton(ui["btn_download"], callback_data="download")
    ])

    if msg.from_user.id == OWNER_ID:
        kb.add(types.InlineKeyboardButton(ui["btn_settings"], callback_data="settings"))

    if start_photo:
        bot.send_photo(msg.chat.id, start_photo, caption=text, reply_markup=kb)
    else:
        bot.send_message(msg.chat.id, text, reply_markup=kb)

# ================= CALLBACK =================
@bot.callback_query_handler(func=lambda c: True)
def cb(c):
    uid = c.from_user.id
    cid = c.message.chat.id

    if c.data == "check_join":
        if is_joined(uid):
            start(c.message)
        else:
            bot.answer_callback_query(c.id, "❌ Join نەبوو", show_alert=True)

    elif c.data == "download":
        wait_link[uid] = True
        bot.send_message(
            cid,
            ui["ask_link"],
            reply_markup=base_kb([
                types.InlineKeyboardButton(ui["btn_close"], callback_data="close")
            ])
        )

    elif c.data == "settings":
        if uid != OWNER_ID:
            return
        kb = types.InlineKeyboardMarkup(row_width=1)
        kb.add(
            types.InlineKeyboardButton("✏️ گۆڕینی پەیامەکان", callback_data="edit_text"),
            types.InlineKeyboardButton("🔘 گۆڕینی دوگمەکان", callback_data="edit_buttons"),
            types.InlineKeyboardButton("📢 گۆڕینی دوگمەی Join", callback_data="edit_join_btn"),
            types.InlineKeyboardButton("🔁 گۆڕینی کەناڵ", callback_data="edit_channel"),
            types.InlineKeyboardButton("🖼 وێنەی Start", callback_data="set_photo"),
            types.InlineKeyboardButton(ui["btn_close"], callback_data="close")
        )
        bot.send_message(cid, "⚙️ Settings (Owner)", reply_markup=kb)

    elif c.data == "edit_text":
        wait_edit[uid] = "text"
        bot.send_message(cid, "✏️ دەقی نوێ بنێرە (emoji + text):")

    elif c.data == "edit_buttons":
        wait_edit[uid] = "buttons"
        bot.send_message(
            cid,
            "✏️ ناوی دوگمەکان بنێرە:\n"
            "download|again|close|settings|owner|join"
        )

    elif c.data == "edit_join_btn":
        wait_edit[uid] = "join_btn"
        bot.send_message(cid, "✏️ ناوی نوێی دوگمەی Join بنێرە:")

    elif c.data == "edit_channel":
        wait_channel[uid] = True
        bot.send_message(cid, "🔁 ناوی کەناڵی نوێ بنێرە (@channel)")

    elif c.data == "set_photo":
        wait_photo[uid] = True
        bot.send_message(cid, "🖼 وێنەی Start بنێرە")

    elif c.data == "close":
        wait_link.pop(uid, None)
        wait_edit.pop(uid, None)
        wait_photo.pop(uid, None)
        wait_channel.pop(uid, None)
        bot.delete_message(cid, c.message.message_id)

# ================= HANDLE TEXT =================
@bot.message_handler(func=lambda m: True)
def handle_text(m):
    uid = m.from_user.id
    cid = m.chat.id

    if uid in wait_channel:
        global CHANNEL_USERNAME
        if m.text.startswith("@"):
            CHANNEL_USERNAME = m.text.strip()
            wait_channel.pop(uid)
            bot.send_message(cid, "✅ کەناڵ گۆڕا")
        else:
            bot.send_message(cid, "❌ ناو بە @ دەست پێ بکە")
        return

    if uid in wait_edit:
        if wait_edit[uid] == "text":
            ui["start"] = m.text
        elif wait_edit[uid] == "buttons":
            try:
                d, a, c, s, o, j = m.text.split("|")
                ui["btn_download"] = d
                ui["btn_again"] = a
                ui["btn_close"] = c
                ui["btn_settings"] = s
                ui["btn_owner"] = o
                ui["btn_join"] = j
            except:
                bot.send_message(cid, "❌ فۆرمات هەڵەیە")
                return
        elif wait_edit[uid] == "join_btn":
            ui["btn_join"] = m.text

        wait_edit.pop(uid)
        bot.send_message(cid, "✅ گۆڕانکاری سەرکەوتوو بوو")
        return

    if uid in wait_link and m.text.startswith("http"):
        bot.send_chat_action(cid, "upload_video")
        bot.send_message(cid, ui["downloading"])
        try:
            ydl_opts = {
                "format": "bestvideo+bestaudio/best",
                "merge_output_format": "mp4",
                "outtmpl": f"{DOWNLOAD_DIR}/%(title).60s.%(ext)s",
                "quiet": True,
                "noplaylist": True,
                "external_downloader": "aria2c",
                "external_downloader_args": ["-x", "16", "-k", "1M"],
                "http_headers": {"User-Agent": "Mozilla/5.0"}
            }
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(m.text, download=True)
                file = ydl.prepare_filename(info)

            with open(file, "rb") as f:
                bot.send_video(cid, f)

            os.remove(file)
            bot.send_message(cid, ui["done"], reply_markup=again_kb())
        except Exception as e:
            bot.send_message(cid, f"{ui['error']}\n{e}")

        wait_link.pop(uid, None)

# ================= HANDLE PHOTO =================
@bot.message_handler(content_types=["photo"])
def handle_photo(m):
    global start_photo
    if m.from_user.id in wait_photo:
        start_photo = m.photo[-1].file_id
        wait_photo.pop(m.from_user.id)
        bot.send_message(m.chat.id, "✅ وێنە گۆڕا")

print("🤖 BOT READY — FAST, FULL, OWNER NOTIFIED")
bot.infinity_polling()