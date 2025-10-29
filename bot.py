import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes
import logging

# 📦 logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# 🔑 توكن لە ڤاریەبڵی پارێزراوە
TOKEN = os.environ.get("8386116524:AAH7UHj8vvsGziJrSHxqsTYcv7KUdumPNNk")

# 🧠 پشکنینی ئەدمین
async def is_admin(update: Update, user_id: int) -> bool:
    member = await update.effective_chat.get_member(user_id)
    return member.status in ["administrator", "creator"]

# 🚀 /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.chat.type != "private":
        await update.message.reply_text("❌ ئەم فەرمانە تەنها لە پرایڤەت کاردەکات.")
        return

    keyboard = [
        [InlineKeyboardButton("➕ زیادکردنی بۆت بۆ گروپ", url=f"https://t.me/{(kawdan context.bot.get_me()).username}?startgroup=true")],
        [InlineKeyboardButton("⚙️ ڕێکخستنەکان", callback_data="settings")]
    ]
    await update.message.reply_text(
        "👋 سڵاو! من بۆتەکەم بۆ تاگکردنی ئەندامان و یارمەتیدان.\n\n"
        "📢 بنووسە @l7n لە گرووپ بۆ دوگمەکان.\n"
        "👑 بنووسە /admin بۆ تاگکردنی ئەدمینەکان.\n"
        "ℹ️ بنووسە /help بۆ زانیاری زیاتر.",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# ⚙️ settings
async def settings_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.message.reply_text("⚙️ هیچ شتێکی ڕێکخستن نیە ئێستا، بە زووانە زیاد دەبێت 💜")

# ℹ️ /help
async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        "📖 *یارمەتی بۆت:*\n\n"
        "🔹 @l7n → نیشاندانی دوگمەکان\n"
        "🔹 @all → تاگکردنی هەموو ئەندامەکان (تەنها ئەدمین)\n"
        "🔹 @stop → وەستاندنی تاگکردن\n"
        "🔹 /admin → تاگکردنی تەنها ئەدمینەکان\n"
        "🔹 /help → ئەم پەیامە\n\n"
        "🧿 بۆتەکەت بە شێوەیەکی تایبەت بۆ گرووپەکان کاردەکات."
    )
    await update.message.reply_text(text, parse_mode="Markdown")

# 📣 @all
async def tag_all(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    chat = update.message.chat

    if not await is_admin(update, user.id):
        await update.message.reply_text("🚫 تەنها ئەدمین دەتوانێ @all بەکاربهێنێت.")
        return

    await update.message.reply_text("📢 دەستپێکرد بە تاگکردنی ئەندامەکان...")

    try:
        members = await context.bot.get_chat_administrators(chat.id)
        text = ""
        for member in members:
            if not member.user.is_bot:
                name = f"@{member.user.username}" if member.user.username else member.user.first_name
                text += f"{name} "
                if len(text) > 300:
                    await update.message.reply_text(text)
                    text = ""
        if text:
            await update.message.reply_text(text)
        await update.message.reply_text("✅ تاگکردن تەواو بوو.")
    except Exception as e:
        await update.message.reply_text(f"⚠️ هەڵەیەک ڕویدا:\n{e}")

# 🛑 @stop
async def stop_tagging(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("⛔ تاگکردن وەستا.")

# 🟣 @l7n
async def show_buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    if not await is_admin(update, user.id):
        await update.message.reply_text("🚫 تەنها ئەدمین دەتوانێ @l7n بەکاربهێنێت.")
        return

    keyboard = [
        [InlineKeyboardButton("🔵 @all", callback_data="tag_all"),
         InlineKeyboardButton("🔴 @stop", callback_data="stop_tag")]
    ]
    await update.message.reply_text("🎛 دوگمەکان:", reply_markup=InlineKeyboardMarkup(keyboard))

# 👑 /admin
async def tag_admins(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.message.chat
    try:
        members = await context.bot.get_chat_administrators(chat.id)
        text = "👑 ئەدمینەکان:\n"
        for member in members:
            if not member.user.is_bot:
                name = f"@{member.user.username}" if member.user.username else member.user.first_name
                text += f"{name} "
        await update.message.reply_text(text)
    except Exception as e:
        await update.message.reply_text(f"⚠️ هەڵەیەک ڕویدا:\n{e}")

# 🎛 دوگمەکان
async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if query.data == "tag_all":
        await tag_all(Update(update.update_id, message=query.message), context)
    elif query.data == "stop_tag":
        await query.message.reply_text("⛔ تاگکردن وەستا.")

# ▶️ ڕاگەیاندن
def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_cmd))
    app.add_handler(CommandHandler("admin", tag_admins))
    app.add_handler(CallbackQueryHandler(settings_callback, pattern="settings"))
    app.add_handler(MessageHandler(filters.TEXT & filters.Regex("@all"), tag_all))
    app.add_handler(MessageHandler(filters.TEXT & filters.Regex("@stop"), stop_tagging))
    app.add_handler(MessageHandler(filters.TEXT & filters.Regex("@l7n"), show_buttons))
    app.add_handler(CallbackQueryHandler(button_callback))

    print("🤖 Bot is running...")
    app.run_polling()

if name == "__main__":
    main()