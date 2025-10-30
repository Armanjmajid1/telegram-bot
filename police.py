import telebot
from telebot import types
import os

# توکەنی خۆت لێرە دانە (یان لە Railway دابنێ بە BOT_TOKEN)
TOKEN = os.getenv("8016109195:AAGjQQlWzhQhmz1dnTZP9IUzoondxLBM4cE") or "PUT_YOUR_TOKEN_HERE"
bot = telebot.TeleBot(TOKEN, parse_mode="HTML")

@bot.message_handler(commands=['start'])
def start(m):
    bot.send_message(m.chat.id,
        "👮‍♂️ سلاو! من بۆتی <b>POLICE</b>م.\n"
        "بۆ بینینی دوگمەکان بنوسە <code>L7N</code> لە گروپەکەت 🧠"
    )

# هەر كات L7N بنوسیت، پەیامە بە دوگمەكان دەردەكەوێت
@bot.message_handler(func=lambda msg: msg.text and msg.text.lower() == "l7n")
def send_l7n_panel(m):
    bot.send_message(m.chat.id, "📦 <b>پەیامی L7N</b>")

    # 🔗 لینكەكان
    link_kb = types.InlineKeyboardMarkup(row_width=2)
    link_kb.add(
        types.InlineKeyboardButton("📤 فه‌كرنا لینك", callback_data="send_link"),
        types.InlineKeyboardButton("📥 گرتنا لینك", callback_data="get_link")
    )
    bot.send_message(m.chat.id, "🔗 <b>لینكەکان</b>", reply_markup=link_kb)

    # 🖼️ وێنه‌كان
    photo_kb = types.InlineKeyboardMarkup(row_width=2)
    photo_kb.add(
        types.InlineKeyboardButton("📤 فه‌كرنا رسما", callback_data="send_photo"),
        types.InlineKeyboardButton("📥 گرتنا رسما", callback_data="get_photo")
    )
    bot.send_message(m.chat.id, "🖼️ <b>وێنەکان</b>", reply_markup=photo_kb)

    # ⚙️ شتە زیاتر
    more_kb = types.InlineKeyboardMarkup(row_width=2)
    more_kb.add(
        types.InlineKeyboardButton("🧹 سڕینەوەی پەیام", callback_data="delete"),
        types.InlineKeyboardButton("ℹ️ زانیاری", callback_data="info")
    )
    bot.send_message(m.chat.id, "⚙️ <b>فەرمانە زیاتر</b>", reply_markup=more_kb)

@bot.callback_query_handler(func=lambda c: True)
def callback(c):
    if c.data == "send_link":
        bot.answer_callback_query(c.id, "📤 فه‌كرنا لینك...")
        bot.send_message(c.message.chat.id, "🔗 لینکەکەت بنووسە:")
    elif c.data == "get_link":
        bot.answer_callback_query(c.id, "📥 گرتنا لینك...")
        bot.send_message(c.message.chat.id, "🔗 ئەمانە لینکەکانت:")
    elif c.data == "send_photo":
        bot.answer_callback_query(c.id, "📤 فه‌كرنا رسما...")
        bot.send_message(c.message.chat.id, "🖼️ وێنە بنێرە:")
    elif c.data == "get_photo":
        bot.answer_callback_query(c.id, "📥 گرتنا رسما...")
        bot.send_message(c.message.chat.id, "🖼️ ئەمانە وێنەکانت:")
    elif c.data == "delete":
        bot.answer_callback_query(c.id, "🧹 پەیام سڕدرایەوە.")
        bot.delete_message(c.message.chat.id, c.message.message_id)
    elif c.data == "info":
        bot.answer_callback_query(c.id, "ℹ️ زانیاری")
        bot.send_message(c.message.chat.id, "🤖 بۆتی Police — ژێر چاوەڕوانی گروپە.")

print("🚀 Police Bot started successfully.")
bot.infinity_polling(timeout=60, long_polling_timeout=60)