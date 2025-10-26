import telebot
from telebot import types
import yt_dlp
import os

TOKEN = "8208886481:AAG389ggLzZPTlAumqJuM0XE8SHW56h5yF8"
bot = telebot.TeleBot(TOKEN, parse_mode="HTML")

os.makedirs("downloads", exist_ok=True)

@bot.message_handler(commands=['start'])
def start(message):
    markup = types.InlineKeyboardMarkup()
    markup.add(
        types.InlineKeyboardButton("🎥 ڤیدیۆ", callback_data="video"),
        types.InlineKeyboardButton("🎵 گۆرانی", callback_data="audio")
    )
    bot.send_message(
        message.chat.id,
        "👋 سڵاو! من بۆتی گۆرانی و ڤیدیۆم.\n"
        "لینکێکی YouTube یان TikTok بنێرە 👇",
        reply_markup=markup
    )

@bot.callback_query_handler(func=lambda c: c.data in ["video", "audio"])
def ask_url(call):
    bot.answer_callback_query(call.id)
    mode = call.data
    msg = bot.send_message(call.message.chat.id, "🔗 لینکەکە بنێرە:")
    bot.register_next_step_handler(msg, lambda m: download_media(m, mode))

def download_media(message, mode):
    url = message.text.strip()
    msg = bot.send_message(message.chat.id, "⏳ دابەزاندن دەستپێدەکات...")
    try:
        ydl_opts = {'outtmpl': 'downloads/%(title)s.%(ext)s', 'quiet': True}
        if mode == "audio":
            ydl_opts['format'] = 'bestaudio/best'
            ydl_opts['postprocessors'] = [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }]
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            file_path = ydl.prepare_filename(info)
            title = info.get("title", "ناونەناس")

        with open(file_path, "rb") as f:
            if mode == "audio":
                bot.send_audio(message.chat.id, f, caption=f"🎶 {title}")
            else:
                bot.send_video(message.chat.id, f, caption=f"🎬 {title}")
        os.remove(file_path)
        bot.delete_message(message.chat.id, msg.id)
        bot.send_message(message.chat.id, "✅ دابەزاندن تەواو بوو!")
    except Exception as e:
        bot.send_message(message.chat.id, f"⚠️ هەڵەیەک ڕویدا:\n{e}")

print("🎵 Music Bot is running...")
bot.infinity_polling()