import telebot
from telebot import types
from datetime import datetime

# ================== CONFIG ==================
TOKEN = "8397765532:AAGdinwgJ7d0e8dM6ND9kGwcAdEclZMFvWg"
BOT_USERNAME = "L77NN_BOT"   # بێ @
OWNER_USERNAME = "L7N07"     # بێ @

bot = telebot.TeleBot(TOKEN)

# ================== STORAGE ==================
ITEMS = {
    "links": "لینک",
    "photos": "وێنە",
    "videos": "ڤیدیۆ",
    "documents": "فایل",
    "stickers": "ستیکەر",
    "gifs": "GIF",
    "voice": "دەنگ",
    "audio": "گۆرانی",
    "forwards": "فۆروارد",
    "mentions": "منشن (@)",
    "badwords": "وشە ناپەسەند",
}

BAD_WORDS = ["sex", "porn", "xxx", "fuck", "pussy", "dick", "ass"]

locks = {}  # chat_id: {key: bool}

def init(chat_id: int):
    if chat_id not in locks:
        locks[chat_id] = {k: False for k in ITEMS.keys()}

def is_admin(chat_id: int, user_id: int) -> bool:
    try:
        m = bot.get_chat_member(chat_id, user_id)
        return m.status in ["administrator", "creator"]
    except:
        return False

# ================== TEXT PAGES (L7N menu) ==================
PAGE_1 = (
"📌 **فەرمانەکان (پەڕە 1/3)**\n\n"
"🛡️ **پانێڵی پاراستن**\n"
"• L7N → دەرخستنی لیست\n"
"• دوگمەکان → قفل/فتح\n\n"
"🔒/🔓 **قفل و فتح**\n"
"• لینک، وێنە، ڤیدیۆ، فایل، ستیکەر\n"
"• GIF، دەنگ، گۆرانی\n"
"• فۆروارد، منشن\n"
"• وشە ناپەسەند\n\n"
"👮 تەنها ئەدمین دەتوانێت قفل/فتح بکات.\n"
)

PAGE_2 = (
"📌 **فەرمانەکان (پەڕە 2/3)**\n\n"
"👮 **فەرمانەکانی ئەدمین (سادە)**\n"
"• /ban (بە Reply) → بلاک\n"
"• /unban (بە Reply) → لابردنی بلاک\n"
"• /mute 10 (بە Reply) → بێدەنگ 10 خولەک\n"
"• /unmute (بە Reply) → لابردنی بێدەنگی\n\n"
"🧹 **پاککردنەوە**\n"
"• قفل بوو → پەیام دەسڕێتەوە\n\n"
"ℹ️ ئەم فەرمانانە تەنها کاردەکەن ئەگەر بۆت Admin بێت.\n"
)

PAGE_3 = (
"📌 **فەرمانەکان (پەڕە 3/3)**\n\n"
"👋 ترحیب (دەستکاری لە داهاتوودا)\n"
"• دەتوانیت پیامێکی ترحیب زیاد بکەیت\n\n"
"🔗 **تێبینییە گرنگەکان**\n"
"• /start تەنها لە پرایڤەتە\n"
"• L7N لە گروپ بنووسە\n"
"• بۆت Admin بکە و Delete messages داگیر بکە\n\n"
"✅ ئەگەر دەتەوێت پەیامەکان و شێواز فخمتر بن، پێم بڵێ.\n"
)

def l7n_text(page: int) -> str:
    return {1: PAGE_1, 2: PAGE_2, 3: PAGE_3}.get(page, PAGE_1)

# ================== KEYBOARDS ==================
def nav_kb(page: int) -> types.InlineKeyboardMarkup:
    kb = types.InlineKeyboardMarkup(row_width=3)
    kb.add(
        types.InlineKeyboardButton("1", callback_data="nav_1"),
        types.InlineKeyboardButton("2", callback_data="nav_2"),
        types.InlineKeyboardButton("3", callback_data="nav_3"),
    )
    kb.add(types.InlineKeyboardButton("🛡️ پانێڵی قفل/فتح", callback_data="open_panel"))
    return kb

def panel_kb(chat_id: int) -> types.InlineKeyboardMarkup:
    init(chat_id)
    kb = types.InlineKeyboardMarkup(row_width=2)

    # دوو بەش: فتح / قفل (وەک داواکاری)
    kb.add(types.InlineKeyboardButton("🟢 بەشی فتح", callback_data="show_open"),
           types.InlineKeyboardButton("🔴 بەشی قفل", callback_data="show_lock"))
    kb.add(types.InlineKeyboardButton("⬅️ گەڕانەوە بۆ لیست", callback_data="back_to_list"))
    return kb

def open_list_kb() -> types.InlineKeyboardMarkup:
    kb = types.InlineKeyboardMarkup(row_width=2)
    kb.add(types.InlineKeyboardButton("⬅️ گەڕانەوە", callback_data="open_panel"))
    for k, name in ITEMS.items():
        kb.add(types.InlineKeyboardButton(f"🟢 فتح {name}", callback_data=f"open_{k}"))
    return kb

def lock_list_kb() -> types.InlineKeyboardMarkup:
    kb = types.InlineKeyboardMarkup(row_width=2)
    kb.add(types.InlineKeyboardButton("⬅️ گەڕانەوە", callback_data="open_panel"))
    for k, name in ITEMS.items():
        kb.add(types.InlineKeyboardButton(f"🔴 قفل {name}", callback_data=f"lock_{k}"))
    return kb

# ================== /start (PRIVATE ONLY) ==================
@bot.message_handler(commands=["start"])
def start(message):
    if message.chat.type != "private":
        return

    kb = types.InlineKeyboardMarkup(row_width=1)
    kb.add(
        types.InlineKeyboardButton("➕ زیادکردنی بۆت بۆ گروپ", url=f"https://t.me/{BOT_USERNAME}?startgroup=true"),
        types.InlineKeyboardButton("👤 چوونە ناو هەژماری سەرۆک", url=f"https://t.me/{OWNER_USERNAME}")
    )
    bot.send_message(
        message.chat.id,
        "👋 **سلاف! بەخێربێیت**\n\n"
        "🛡️ ئەم بۆتە بۆ پاراستنی گروپ ـە.\n\n"
        "📌 لە گروپ بنوسە: **L7N**\n"
        "→ لیست و پانێڵ دێت.\n",
        parse_mode="Markdown",
        reply_markup=kb
    )

# ================== L7N MENU (GROUP) ==================
@bot.message_handler(func=lambda m: m.text and m.text.strip() == "L7N")
def show_l7n(message):
    # تەنها ئەدمین بتوانێت لیست و پانێڵ دەرخات
    if not is_admin(message.chat.id, message.from_user.id):
        return

    bot.send_message(
        message.chat.id,
        l7n_text(1),
        parse_mode="Markdown",
        reply_markup=nav_kb(1)
    )

# ================== CALLBACK NAV + PANEL ==================
@bot.callback_query_handler(func=lambda c: True)
def callbacks(c):
    chat_id = c.message.chat.id
    user_id = c.from_user.id

    # نا-ئەدمین
    if not is_admin(chat_id, user_id):
        bot.answer_callback_query(c.id, "🚫 تەنها ئەدمین")
        return

    data = c.data

    # Navigation pages
    if data.startswith("nav_"):
        page = int(data.split("_")[1])
        bot.edit_message_text(
            l7n_text(page),
            chat_id=chat_id,
            message_id=c.message.message_id,
            parse_mode="Markdown",
            reply_markup=nav_kb(page)
        )
        bot.answer_callback_query(c.id, "✅")
        return

    # Open main panel
    if data == "open_panel":
        bot.edit_message_text(
            "🛡️ **پانێڵی پاراستن**\n\n"
            "🔴 قفل = ڕێگریکردن\n"
            "🟢 فتح = ڕێگەدان\n\n"
            "دوگمە هەڵبژێرە:",
            chat_id=chat_id,
            message_id=c.message.message_id,
            parse_mode="Markdown",
            reply_markup=panel_kb(chat_id)
        )
        bot.answer_callback_query(c.id, "✅")
        return

    if data == "back_to_list":
        bot.edit_message_text(
            l7n_text(1),
            chat_id=chat_id,
            message_id=c.message.message_id,
            parse_mode="Markdown",
            reply_markup=nav_kb(1)
        )
        bot.answer_callback_query(c.id, "✅")
        return

    if data == "show_open":
        bot.edit_message_text(
            "🟢 **بەشی فتح**\nکلیک بکە بۆ کرانەوەی شتان:",
            chat_id=chat_id,
            message_id=c.message.message_id,
            parse_mode="Markdown",
            reply_markup=open_list_kb()
        )
        bot.answer_callback_query(c.id, "✅")
        return

    if data == "show_lock":
        bot.edit_message_text(
            "🔴 **بەشی قفل**\nکلیک بکە بۆ داخستن/قفلکردنی شتان:",
            chat_id=chat_id,
            message_id=c.message.message_id,
            parse_mode="Markdown",
            reply_markup=lock_list_kb()
        )
        bot.answer_callback_query(c.id, "✅")
        return

    # Toggle lock/open
    if data.startswith(("lock_", "open_")):
        init(chat_id)
        action, key = data.split("_", 1)
        locks[chat_id][key] = True if action == "lock" else False
        bot.answer_callback_query(
            c.id,
            f"{ITEMS[key]} " + ("قفل کرا 🔴" if action == "lock" else "کرایەوە 🟢")
        )
        return

    bot.answer_callback_query(c.id, "✅")

# ================== PROTECTION (DELETE) ==================
@bot.message_handler(content_types=[
    "text","photo","video","document","sticker","animation","voice","audio"
])
def protect(message):
    chat_id = message.chat.id
    init(chat_id)

    # ئەدمین نەسڕێتەوە
    if is_admin(chat_id, message.from_user.id):
        return

    # Links
    if locks[chat_id]["links"] and message.content_type == "text" and message.text:
        if "http" in message.text or "t.me" in message.text:
            try: bot.delete_message(chat_id, message.message_id)
            except: pass
            return

    # Photos
    if locks[chat_id]["photos"] and message.content_type == "photo":
        try: bot.delete_message(chat_id, message.message_id)
        except: pass
        return# Videos
    if locks[chat_id]["videos"] and message.content_type == "video":
        try: bot.delete_message(chat_id, message.message_id)
        except: pass
        return

    # Documents
    if locks[chat_id]["documents"] and message.content_type == "document":
        try: bot.delete_message(chat_id, message.message_id)
        except: pass
        return

    # Stickers
    if locks[chat_id]["stickers"] and message.content_type == "sticker":
        try: bot.delete_message(chat_id, message.message_id)
        except: pass
        return

    # GIFs (animation)
    if locks[chat_id]["gifs"] and message.content_type == "animation":
        try: bot.delete_message(chat_id, message.message_id)
        except: pass
        return

    # Voice
    if locks[chat_id]["voice"] and message.content_type == "voice":
        try: bot.delete_message(chat_id, message.message_id)
        except: pass
        return

    # Audio
    if locks[chat_id]["audio"] and message.content_type == "audio":
        try: bot.delete_message(chat_id, message.message_id)
        except: pass
        return

    # Forwards (best-effort)
    if locks[chat_id]["forwards"]:
        if getattr(message, "forward_from", None) or getattr(message, "forward_from_chat", None):
            try: bot.delete_message(chat_id, message.message_id)
            except: pass
            return

    # Mentions
    if locks[chat_id]["mentions"] and message.content_type == "text" and message.text:
        if "@" in message.text:
            try: bot.delete_message(chat_id, message.message_id)
            except: pass
            return

    # Bad words
    if locks[chat_id]["badwords"] and message.content_type == "text" and message.text:
        t = message.text.lower()
        if any(w in t for w in BAD_WORDS):
            try: bot.delete_message(chat_id, message.message_id)
            except: pass
            return

# ================== SIMPLE ADMIN TOOLS (OPTIONAL) ==================
@bot.message_handler(commands=["ban","unban","mute","unmute"])
def admin_tools(message):
    if not is_admin(message.chat.id, message.from_user.id):
        return

    if not message.reply_to_message:
        bot.reply_to(message, "⚠️ ئەم فەرمانە بە Reply بکە بۆ پەیامی کەسەکە.")
        return

    target_id = message.reply_to_message.from_user.id
    cmd = message.text.split()

    try:
        if cmd[0] == "/ban":
            bot.ban_chat_member(message.chat.id, target_id)
            bot.reply_to(message, "✅ بلاک کرا")
        elif cmd[0] == "/unban":
            bot.unban_chat_member(message.chat.id, target_id)
            bot.reply_to(message, "✅ بلاک لابرا")
        elif cmd[0] == "/mute":
            minutes = int(cmd[1]) if len(cmd) > 1 else 10
            until = int(datetime.now().timestamp()) + minutes * 60
            bot.restrict_chat_member(
                message.chat.id, target_id,
                until_date=until,
                permissions=types.ChatPermissions(can_send_messages=False)
            )
            bot.reply_to(message, f"✅ بێدەنگ کرا بۆ {minutes} خولەک")
        elif cmd[0] == "/unmute":
            bot.restrict_chat_member(
                message.chat.id, target_id,
                permissions=types.ChatPermissions(
                    can_send_messages=True,
                    can_send_media_messages=True,
                    can_send_other_messages=True,
                    can_add_web_page_previews=True
                )
            )
            bot.reply_to(message, "✅ بێدەنگی لابرا")
    except Exception as e:
        bot.reply_to(message, f"⚠️ هەڵە: {e}")

print("🤖 Bot is running...")
bot.infinity_polling()