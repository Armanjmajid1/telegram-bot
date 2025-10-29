# -*- coding: utf-8 -*-
import telebot
from telebot import types
import json
import os

TOKEN = "توكنەکەت_لێرە_بنوسە"
bot = telebot.TeleBot(TOKEN, parse_mode="HTML")

DATA_FILE = "started_users.json"

if os.path.exists(DATA_FILE):
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        started_users = json.load(f)
else:
    started_users = {}

def save_users():
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(started_users, f, ensure_ascii=False, indent=2)

# 📍 /start Command
@bot.message_handler(commands=["start"])
def start(message):
    user_id = str(message.from_user.id)
    name = message.from_user.first_name or "دووست"

    if user_id not in started_users:
        markup = types.InlineKeyboardMarkup(row_width=3)
        btn_kurdi = types.InlineKeyboardButton("🇹🇯 كوردی", callback_data="lang_kurdi")
        btn_arabic = types.InlineKeyboardButton("🇸🇦 عربي", callback_data="lang_arabic")
        btn_english = types.InlineKeyboardButton("🇬🇧 English", callback_data="lang_english")
        markup.add(btn_kurdi, btn_arabic, btn_english)

        bot.send_message(
            message.chat.id,
            f"👋 <b>سڵاو {name}!</b>\n\n"
            f"✨ بەخێربێیت بۆ <b>L7N Bot</b>\n\n"
            f"🌍 تكايە زمانێك هەلبژێرە بۆ بەردەوامبوون 👇",
            reply_markup=markup,
        )
    else:
        lang = started_users[user_id]["lang"]
        send_greeting(message.chat.id, name, lang)

# 🌐 زمان هەلبژێرە
@bot.callback_query_handler(func=lambda c: c.data.startswith("lang_"))
def select_language(call):
    user_id = str(call.from_user.id)
    lang = call.data.split("_")[1]
    started_users[user_id] = {"lang": lang}
    save_users()

    name = call.from_user.first_name or "دووست"
    send_greeting(call.message.chat.id, name, lang, edit=call)

# 🎨 پەیامی بەخێربێیت بە زمانەکانی جیاواز
def send_greeting(chat_id, name, lang, edit=None):
    markup = types.InlineKeyboardMarkup(row_width=2)
    btn_channel = types.InlineKeyboardButton("📢 كەناڵ", url="https://t.me/L7Nchannal")
    btn_owner = types.InlineKeyboardButton("👑 وەنا", url="https://t.me/l7n07")
    btn_fonts = types.InlineKeyboardButton("🌈 فۆنتە جوانەکان", callback_data="fonts")
    btn_setting = types.InlineKeyboardButton("⚙️ ستينگ", callback_data="settings")
    markup.add(btn_channel, btn_owner)
    markup.add(btn_fonts, btn_setting)

    if lang == "kurdi":
        text = (
            f"✨ <b>سڵاو {name}!</b>\n\n"
            "بەخێربێیت بۆ <b>L7N Bot</b> 🤖\n"
            "بۆتی فۆنت و جوانکاری ناو ✨\n\n"
            "📎 جوین بکە بە کەناڵ و وەنا بۆ بەردەوامبوون 👇"
        )
    elif lang == "arabic":
        text = (
            f"✨ <b>مرحباً {name}!</b>\n\n"
            "مرحباً بك في <b>L7N Bot</b> 🤖\n"
            "بوت الخطوط والزخرفة ✨\n\n"
            "📎 انضم إلى القناة أو تواصل مع المالك 👇"
        )
    else:
        text = (
            f"✨ <b>Hello {name}!</b>\n\n"
            "Welcome to <b>L7N Bot</b> 🤖\n"
            "Font & Decoration Bot ✨\n\n"
            "📎 Join the channel or contact the owner 👇"
        )

    if edit:
        bot.edit_message_text(text, chat_id, edit.message.message_id, reply_markup=markup)
    else:
        bot.send_message(chat_id, text, reply_markup=markup)

# 🌈 فۆنتە جوانەکان
@bot.callback_query_handler(func=lambda c: c.data == "fonts")
def fonts_list(call):
    fonts = [
        "Ａｒｍａｎ", "𝔄𝔯𝔪𝔞𝔫", "𝒜𝓇𝓂𝒶𝓃", "𝓐𝓻𝓶𝓪𝓷", "𝕬𝖗𝖒𝖆𝖓",
        "ᴀʀᴍᴀɴ", "𝐀𝐫𝐦𝐚𝐧", "🅰🆁🅼🅰🅽", "ᗩᖇᗰᗩᑎ", "𝙰𝚛𝚖𝚊𝚗",
        "₳Ɽ₥₳₦", "ꪖꪜꪖꪀ", "ᎯᏒᎷᏗᏁ"
    ]
    msg = "🎨 <b>فۆنتە جوانەکان:</b>\n\n" + "\n".join(fonts)
    bot.send_message(call.message.chat.id, msg)

# ⚙️ ستینگ
@bot.callback_query_handler(func=lambda c: c.data == "settings")
def settings(call):
    markup = types.InlineKeyboardMarkup(row_width=2)
    btn_lang = types.InlineKeyboardButton("🌍 گۆرینی زمان", callback_data="change_lang")
    btn_close = types.InlineKeyboardButton("❌ داخستن", callback_data="close")
    markup.add(btn_lang, btn_close)
    bot.send_message(call.message.chat.id, "⚙️ ئەمە ستینگەکەیە:", reply_markup=markup)

@bot.callback_query_handler(func=lambda c: c.data == "change_lang")
def change_language(call):
    start(call.message)

@bot.callback_query_handler(func=lambda c: c.data == "close")
def close(call):
    bot.delete_message(call.message.chat.id, call.message.message_id)

bot.infinity_polling()