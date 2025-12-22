import telebot
from telebot import types
import time

TOKEN = "8502306914:AAGtTWs7lgrAVuwUKxClvyf6o38BSC9_nNg"
OWNER_ID = 6583637773

bot = telebot.TeleBot(TOKEN, parse_mode="HTML")

# ================== STORAGE ==================
LANG = {}            # chat_id -> "ku" | "ar"
ACTIVE = {}          # chat_id -> True/False
CHANNELS = {}        # chat_id -> {1:"@ch",2:"@ch"}
JOIN_TEXT = {}       # chat_id -> {1:text,2:text}
JOIN_PHOTO = {}      # chat_id -> file_id

# ================== HELPERS ==================
def is_admin(chat_id, user_id):
    try:
        m = bot.get_chat_member(chat_id, user_id)
        return m.status in ["administrator", "creator"]
    except:
        return False

def L(chat_id, ku, ar):
    return ku if LANG.get(chat_id, "ku") == "ku" else ar

# ================== START ==================
@bot.message_handler(commands=["start"])
def start(m):
    if m.chat.type != "private":
        return
    LANG[m.chat.id] = "ku"
    kb = types.InlineKeyboardMarkup()
    kb.add(
        types.InlineKeyboardButton("🇹🇯 کوردی", callback_data="lang_ku"),
        types.InlineKeyboardButton("🇸🇦 عربي", callback_data="lang_ar")
    )
    bot.send_message(
        m.chat.id,
        "👋 <b>بەخێربێیت بۆ بۆتی Join</b>\n\n"
        "🔹 ئەم بۆتە بۆ پاراستنی گرووپەکەتە\n"
        "🔹 ئەندام دەبێت Joinی کەناڵەکان بکات\n\n"
        "👇 زمان هەلبژێرە",
        reply_markup=kb
    )

# ================== LANGUAGE ==================
@bot.callback_query_handler(func=lambda c: c.data.startswith("lang_"))
def set_lang(c):
    LANG[c.message.chat.id] = c.data.split("_")[1]
    bot.edit_message_text(
        L(c.message.chat.id,
          "✅ زمان کوردی هەڵبژێردرا",
          "✅ تم اختيار اللغة العربية"),
        c.message.chat.id,
        c.message.message_id
    )

# ================== ON / OFF ==================
@bot.message_handler(commands=["on","off"], chat_types=["group","supergroup"])
def onoff(m):
    if not is_admin(m.chat.id, m.from_user.id):
        return
    ACTIVE[m.chat.id] = m.text == "/on"
    bot.send_message(
        m.chat.id,
        L(m.chat.id,
          "✅ بۆت چالاک کرا",
          "✅ تم تفعيل البوت") if m.text=="/on" else
        L(m.chat.id,
          "⛔ بۆت ناچالاک کرا",
          "⛔ تم إيقاف البوت")
    )

# ================== ADD CHANNEL ==================
@bot.message_handler(regexp="^@")
def add_channel(m):
    if m.chat.type == "private":
        return
    if not is_admin(m.chat.id, m.from_user.id):
        return

    CHANNELS.setdefault(m.chat.id, {})
    if len(CHANNELS[m.chat.id]) >= 2:
        bot.send_message(m.chat.id, "⚠️ تەنها ٢ کەناڵ")
        return

    idx = len(CHANNELS[m.chat.id]) + 1
    CHANNELS[m.chat.id][idx] = m.text.strip()
    JOIN_TEXT.setdefault(m.chat.id, {})[idx] = "تکایە Join بکە"

    bot.send_message(m.chat.id, f"✅ کەناڵ {idx} زیادکرا")

# ================== SAVE JOIN PHOTO ==================
@bot.message_handler(content_types=["photo"])
def save_photo(m):
    if m.chat.type != "private":
        return
    JOIN_PHOTO[m.chat.id] = m.photo[-1].file_id
    bot.send_message(m.chat.id, "🖼️ وێنەی Join هەڵگیرا")

# ================== CHECK JOIN ==================
@bot.message_handler(content_types=["text","photo","video","voice","document"])
def check_join(m):
    if m.chat.type == "private":
        return
    if not ACTIVE.get(m.chat.id):
        return
    if not CHANNELS.get(m.chat.id):
        return

    for idx,ch in CHANNELS[m.chat.id].items():
        try:
            mem = bot.get_chat_member(ch, m.from_user.id)
            if mem.status in ["left","kicked"]:
                raise Exception
        except:
            try:
                bot.delete_message(m.chat.id, m.message_id)
            except:
                pass

            kb = types.InlineKeyboardMarkup()
            kb.add(types.InlineKeyboardButton(
                L(m.chat.id,"🔗 Join کەناڵ","🔗 الانضمام للقناة"),
                url=f"https://t.me/{ch.replace('@','')}"
            ))

            text = JOIN_TEXT[m.chat.id][idx] + f"\n\n👤 <b>{m.from_user.first_name}</b>"
            if JOIN_PHOTO.get(m.chat.id):bot.send_photo(m.chat.id, JOIN_PHOTO[m.chat.id], caption=text, reply_markup=kb)
            else:
                bot.send_message(m.chat.id, text, reply_markup=kb)
            return

# ================== SETTINGS (OWNER) ==================
@bot.message_handler(commands=["settings"])
def settings(m):
    if m.from_user.id != OWNER_ID:
        return
    kb = types.InlineKeyboardMarkup()
    kb.add(
        types.InlineKeyboardButton("🧹 Reset", callback_data="reset"),
        types.InlineKeyboardButton("📊 Status", callback_data="status")
    )
    bot.send_message(m.chat.id, "⚙️ Settings", reply_markup=kb)

@bot.callback_query_handler(func=lambda c: c.data in ["reset","status"])
def owner_actions(c):
    if c.from_user.id != OWNER_ID:
        return
    if c.data == "reset":
        ACTIVE.clear(); CHANNELS.clear()
        bot.answer_callback_query(c.id, "Reset Done")
    else:
        bot.answer_callback_query(c.id, f"Groups: {len(ACTIVE)}")

# ================== RUN ==================
bot.infinity_polling()