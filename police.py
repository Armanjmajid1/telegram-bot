# PolîsBot — Full Guard (telebot)
# pip install pyTelegramBotAPI
import time
import re
from collections import defaultdict, deque
import telebot
from telebot import types

TOKEN = "8016109195:AAGjQQlWzhQhmz1dnTZP9IUzoondxLBM4cE"   # ← توکینی بۆتەکەت لێرە بنووسە
bot = telebot.TeleBot(TOKEN)

# ---------- state ----------
locks = {}  # per chat locks
# default lock keys:
DEFAULT_KEYS = [
    "links","photos","git","sex","videos","voice","files","stickers","gifs","media",
    "exefiles"  # apk/exe/zip/rar/7z...
]

# flood & spam settings per chat
spam_length_threshold = defaultdict(lambda: 800)  # if text length > threshold => delete+warn
flood_limits = defaultdict(lambda: (5, 8))  # (max_messages, seconds_window)
flood_mute_seconds = defaultdict(lambda: 60)  # how long to mute violator

# user message timestamps per chat for flood
user_msgs = defaultdict(lambda: defaultdict(lambda: deque()))  # user_msgs[chat_id][user_id] = deque(timestamps)

# helpers
def init_locks(chat_id):
    if chat_id not in locks:
        locks[chat_id] = {k: False for k in DEFAULT_KEYS}

def is_admin(chat_id, user_id):
    try:
        m = bot.get_chat_member(chat_id, user_id)
        return m.status in ["administrator", "creator"]
    except:
        return False

# ---------- admin menu (L7N) ----------
@bot.message_handler(func=lambda m: m.text and m.text.lower() == "l7n")
def send_lock_menu(message):
    if message.chat.type not in ["group","supergroup"]:
        return
    init_locks(message.chat.id)
    if not is_admin(message.chat.id, message.from_user.id):
        bot.reply_to(message, "🚫 تەنها ئەدمین دەتوانێ ئەم فەرمانە بەکاربهێنێت.")
        return

    kb = types.InlineKeyboardMarkup(row_width=2)
    # 10 feature locks (lock/unlock)
    pairs = [
        ("🔒/🔓 لینك", "links"),
        ("🔒/🔓 ڕەسم", "photos"),
        ("🔒/🔓 Git", "git"),
        ("🔒/🔓 سکسی", "sex"),
        ("🔒/🔓 ڤیدیۆ", "videos"),
        ("🔒/🔓 ڤۆیس", "voice"),
        ("🔒/🔓 فایل", "files"),
        ("🔒/🔓 استیکر", "stickers"),
        ("🔒/🔓 گیف", "gifs"),
        ("🔒/🔓 میدیا", "media"),
    ]
    for label, key in pairs:
        kb.add(types.InlineKeyboardButton(label + f" ({'ON' if locks[message.chat.id].get(key) else 'OFF'})", callback_data=f"toggle:{key}"))

    # extra: exefiles (apk/exe/zip)
    kb.add(types.InlineKeyboardButton("🔒/🔓 فایل‌نایاسای (.apk/.exe/.zip)", callback_data="toggle:exefiles"))

    # lock all / unlock all
    kb.add(types.InlineKeyboardButton("🛡️ قفل گشتی 🔒", callback_data="lock_all"),
           types.InlineKeyboardButton("🔓 فەکەرنا گشتی 🔓", callback_data="unlock_all"))

    bot.reply_to(message, "👮‍♂️ سیستەمی پاراستن — هەڵبژێرە تایبەتمەندی بۆ قفل یان فەکران:", reply_markup=kb)

@bot.callback_query_handler(func=lambda c: True)
def callback_query(c):
    chat_id = c.message.chat.id
    user_id = c.from_user.id
    if not is_admin(chat_id, user_id):
        bot.answer_callback_query(c.id, "🚫 تەنها ئەدمین دەتوانێ ئەم کارە بکات.", show_alert=True)
        return
    init_locks(chat_id)
    data = c.data

    if data.startswith("toggle:"):
        key = data.split(":",1)[1]
        locks[chat_id][key] = not locks[chat_id].get(key, False)
        bot.answer_callback_query(c.id, f"🔧 {key} is now {'ON' if locks[chat_id][key] else 'OFF'}")
        # edit to reflect status (optional)
        try:
            bot.edit_message_reply_markup(chat_id, c.message.message_id, reply_markup=None)
        except:
            pass
        return

    if data == "lock_all":
        for k in locks[chat_id]:
            locks[chat_id][k] = True
        bot.answer_callback_query(c.id, "🛡️ هەموو قفڵەکان چالاک کران!")
        return

    if data == "unlock_all":
        for k in locks[chat_id]:
            locks[chat_id][k] = False
        bot.answer_callback_query(c.id, "🔓 هەموو قفڵەکان فەکران!")
        return

# ---------- moderation helpers ----------
def delete_and_warn(chat_id, user_id, message_id, reason_text):
    try:
        bot.delete_message(chat_id, message_id)
    except:
        pass
    try:
        bot.send_message(chat_id, f"⚠️ @{bot.get_chat_member(chat_id, user_id).user.username or bot.get_chat_member(chat_id, user_id).user.first_name}, {reason_text}")
    except:
        # fallback
        bot.send_message(chat_id, "⚠️ پەیامەکە سڕدرا (هۆک: {})".format(reason_text))

def mute_user(chat_id, user_id, seconds):
    try:
        until = int(time.time()) + seconds
        bot.restrict_chat_member(chat_id, user_id, can_send_messages=False, until_date=until)
        bot.send_message(chat_id, f"🔇 بەکارهێنەرەکە مۆد کرا بۆ {seconds} چرکە.")
    except Exception as e:
        print("mute err:", e)

# ---------- flood tracking ----------
def check_flood(chat_id, user_id):
    max_msgs, window = flood_limits[chat_id]
    dq = user_msgs[chat_id][user_id]
    now = time.time()
    dq.append(now)
    # pop old
    while dq and dq[0] < now - window:
        dq.popleft()
    if len(dq) > max_msgs:
        return True
    return False

# ---------- message handler: main protection ----------
@bot.message_handler(content_types=['text','photo','video','voice','document','sticker','animation'])
def protect(message):
    chat_id = message.chat.id
    if message.chat.type not in ["group","supergroup"]:
        return

    init_locks(chat_id)
    user_id = message.from_user.id

    # admins exempt
    if is_admin(chat_id, user_id):
        return

    text = (message.caption or message.text or "").strip()

    # 1) links
    if locks[chat_id].get("links") and re.search(r"(https?://|t\.me/|www\.)", text, re.I):
        delete_and_warn(chat_id, user_id, message.message_id, "ناتوانیت لینک بنێریت — تەنها ئەدمین دەتوانێ.")
        return

    # 2) photos
    if locks[chat_id].get("photos") and message.photo:
        delete_and_warn(chat_id, user_id, message.message_id, "ناتوانیت وێنە بنێریت.")
        return

    # 3) git
    if locks[chat_id].get("git") and re.search(r"(github\.com|gitlab\.com)", text, re.I):
        delete_and_warn(chat_id, user_id, message.message_id, "ناتوانیت لینکی گیت بنێریت.")
        return

    # 4) sex words
    if locks[chat_id].get("sex") and re.search(r"\b(sex|xxx|nude|裸)\b", text, re.I):
        delete_and_warn(chat_id, user_id, message.message_id, "کەرەستە و مەواد نایاسا قەدەغە کراون.")
        return

    # 5) videos
    if locks[chat_id].get("videos") and message.video:
        delete_and_warn(chat_id, user_id, message.message_id, "ناتوانیت ڤیدیۆ بنێریت.")
        return

    # 6) voice
    if locks[chat_id].get("voice") and (message.voice or message.audio):
        delete_and_warn(chat_id, user_id, message.message_id, "ناتوانیت ڤۆیس یان ڕێکەوتە بنێریت.")
        return

    # 7) files (document)
    if locks[chat_id].get("files") and message.document:
        delete_and_warn(chat_id, user_id, message.message_id, "ناتوانیت فایل بنێریت.")
        return

    # 8) stickers
    if locks[chat_id].get("stickers") and message.sticker:
        delete_and_warn(chat_id, user_id, message.message_id, "ناتوانیت استیکەر بنێریت.")
        return

    # 9) gifs
    if locks[chat_id].get("gifs") and message.animation:
        delete_and_warn(chat_id, user_id, message.message_id, "ناتوانیت گیف بنێریت.")
        return

    # 10) media (any)
    if locks[chat_id].get("media") and (message.photo or message.video or message.document):
        delete_and_warn(chat_id, user_id, message.message_id, "ناتوانیت میدیا بنێریت.")
        return

    # 11) exefiles (.apk .exe .zip .rar .7z)
    if locks[chat_id].get("exefiles") and message.document:
        fname = (message.document.file_name or "").lower()
        if any(fname.endswith(ext) for ext in [".apk",".exe",".zip",".rar",".7z"]):
            delete_and_warn(chat_id, user_id, message.message_id, "بارکردنی ئەم جۆر فایڵان قەدەغەیە.")
            return

    # 12) spam length
    if text and len(text) >= spam_length_threshold[chat_id]:
        delete_and_warn(chat_id, user_id, message.message_id, "پەیامە درێژەکان وەک سپام پێناسە دەکرێن — تکایە خێرا بنووسە.")
        return

    # 13) flood (rate limit)
spam_length_threshold = defaultdict(lambda: 800)
flood_limits = defaultdict(lambda: (5, 8))  # max_messages, seconds window
flood_mute_seconds = defaultdict(lambda: 60)  # how long to mute violator
flood_rate = defaultdict(lambda: 0)  # current flood rate tracker

# ---------- optional admin commands to configure ----------
@bot.message_handler(commands=['set_spam_len'])
def cmd_set_spam(message):
    if not is_admin(message.chat.id, message.from_user.id):
        return
    parts = message.text.split()
    if len(parts) >= 2 and parts[1].isdigit():
        spam_length_threshold[message.chat.id] = int(parts[1])
        bot.reply_to(message, f"✅ Threshold set to {parts[1]} chars.")
    else:
        bot.reply_to(message, "Usage: /set_spam_len 800")

@bot.message_handler(commands=['set_flood'])
def cmd_set_flood(message):
    if not is_admin(message.chat.id, message.from_user.id):
        return
    parts = message.text.split()
    if len(parts) >= 3 and parts[1].isdigit() and parts[2].isdigit():
        flood_limits[message.chat.id] = (int(parts[1]), int(parts[2]))
        bot.reply_to(message, f"✅ Flood set to {parts[1]} msgs / {parts[2]} sec")
    else:
        bot.reply_to(message, "Usage: /set_flood <max_msgs> <seconds>")

@bot.message_handler(commands=['set_mute'])
def cmd_set_mute(message):
    if not is_admin(message.chat.id, message.from_user.id):
        return
    parts = message.text.split()
    if len(parts) >= 2 and parts[1].isdigit():
        flood_mute_seconds[message.chat.id] = int(parts[1])
        bot.reply_to(message, f"✅ Mute time set to {parts[1]} seconds")
    else:
        bot.reply_to(message, "Usage: /set_mute <seconds>")

# ---------- start ----------
print("🚔 PolîsBot running with extended protections...")
bot.infinity_polling()