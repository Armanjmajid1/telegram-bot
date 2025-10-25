
from telebot import types

# 🔑 زانیاری بۆت
TOKEN = "8000635137:AAE9bKrh3e8fdG1OzS0yUkJAhgZwxbZxet0"
OWNER_USERNAME = "@armanj_majed"
PHOTO_URL = "https://files.catbox.moe/junrzs.png"

bot = telebot.TeleBot(TOKEN, threaded=True, num_threads=50)  # ⚡ خێراتر کردنی بۆت


# ⚡ /start فەرمان
@bot.message_handler(commands=['start'])
def start_cmd(message):
    user = message.from_user

    markup = types.InlineKeyboardMarkup(row_width=2)

    add_group = types.InlineKeyboardButton(
        "➕ زیادکردنی بۆت بۆ گروپ",
        url=f"https://t.me/{bot.get_me().username}?startgroup=true"
    )
    owner_button = types.InlineKeyboardButton(
        "👑 پەیوەندی بە خاوەن بۆت",
        url=f"https://t.me/{OWNER_USERNAME.strip('@')}"
    )
    markup.add(add_group, owner_button)

    # 🔗 چوار کەناڵ
    channels = [
        ("📢 کەناڵی یەکەم", "https://t.me/kawdan"),
        ("📢 کەناڵی دووەم", "https://t.me/kurdishtop1"),
        ("📢 کەناڵی سێیەم", "https://t.me/kurdishtop2"),
        ("📢 کەناڵی چوارەم", "https://t.me/kurdishtop3"),
    ]
    for name, url in channels:
        markup.add(types.InlineKeyboardButton(name, url=url))

    # ⚙️ دوگمەکانی تر
    markup.add(
        types.InlineKeyboardButton("⚙️ گۆڕینی ناوی بۆت", callback_data="edit_name"),
        types.InlineKeyboardButton("❌ ناچالاککردنی بۆت", callback_data="off_bot")
    )

    text = (
        f"👋 سڵاو {user.first_name}!\n\n"
        "🌺 بەخێربێیت بۆ *Kurdistan Group Manager Bot*\n\n"
        "🌀 بۆ بەکاربردنی بۆت:\n"
        "1️⃣ زیاد بکە بۆ گروپەکەت.\n"
        "2️⃣ بنووسە on بۆ چالاککردن.\n"
        "3️⃣ ئەگەر ئەدمین نیت لە کەناڵ، بۆت کار ناکات.\n\n"
        "❌ بۆ ناچالاککردن بنووسە off.\n\n"
        "⚡ بۆتت بە فەرمی و خێرا کار دەکات، هەر لە تێلی شەودا 💨"
    )

    bot.send_photo(
        message.chat.id,
        PHOTO_URL,
        caption=text,
        parse_mode="Markdown",
        reply_markup=markup
    )


# 🟢 فەرمان ON — چالاککردنی بۆت
@bot.message_handler(func=lambda m: m.text and m.text.lower() == "on")
def activate_bot(message):
    bot.reply_to(message, "✅ بۆت بە سەرکەوتووی چالاک کرا و ئامادەیە بۆ کارکردن ⚡")


# 🔴 فەرمان OFF — ناچالاککردنی بۆت
@bot.message_handler(func=lambda m: m.text and m.text.lower() == "off")
def deactivate_bot(message):
    bot.reply_to(message, "🔴 بۆت ناچالاک کرا. ❌")


# 🧠 Handling errors silently
@bot.message_handler(func=lambda message: True)
def handle_all(message):
    pass  # نەتەوێ تاخیر بکات

# ▶️ دەستپێکردن
print("🤖 بۆت بە خێرایی چالاکە 🔥 (FAST MODE)")
bot.infinity_polling(timeout=10, long_polling_timeout=5)