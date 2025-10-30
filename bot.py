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
def start(message):
    markup = types.InlineKeyboardMarkup(row_width=1)
    add_group = types.InlineKeyboardButton("➕ زیادکردنی بۆت بۆ گروپ", url="https://t.me/YOUR_BOT_USERNAME?startgroup=true")
    contact_button = types.InlineKeyboardButton("📞 👑𝐎𝐰𝐧𝐞𝐫👑", url="https://t.me/L7N07")  # 🔹 ئەمە لینکی پڕۆفایلە
    markup.add(add_group, contact_button)
    
    bot.send_message(
        message.chat.id,
        "👋 سلاف!\n\n"
        "ئه ف بوته تايبه ته بو تاكرنا هه مي انداميت گروپي.\n"
        "📌 بۆ دروستكرنا  بۆتي:\n"
        "➕ بۆتە زیده بكه بو گروپي خو\n"
        "💬 بنوسە @all بۆ تاگ كرنا ئەندامان\n"
        "✋ بنوسە @off بۆ ستوب كرنا تاگئ\n\n"
        "👇 کليك بكه بو زيده كرنا گروپي يأن هه ر اريشه كئ سه روك بوت:",
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
        bot.reply_to(message, "⛔️ تاگکردن ناچالاکە! بۆ چالاککردن بنوسە /start لە پرایڤەت.")
        return

    bot.reply_to(message, "📢 نوكه بوت كار دكه ت بو تاگ كرنا انداما...")

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

        bot.send_message(chat_id, "✅ تاگ كرن خلاس بو.")
    except Exception as e:
        bot.send_message(chat_id, f"⚠️ هەڵەیەک ڕویدا:\n{e}")

# 📴 @off — تاگ هاته ستوب كرن
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