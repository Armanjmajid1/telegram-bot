import telebot
from telebot import types
import time

BOT_TOKEN = "8000635137:AAE9bKrh3e8fdG1OzS0yUkJAhgZwxbZxet0"
bot = telebot.TeleBot(BOT_TOKEN)

# هەر گرووپێک → لیستی کەناڵەکانی خۆی
group_channels = {}

# 🟢 فرمانی start ل پریفات
@bot.message_handler(commands=['start'])
def start_private(message):
    if message.chat.type == "private":
        markup = types.InlineKeyboardMarkup()
        add_bot = types.InlineKeyboardButton("➕ زیادکردنی بۆت بۆ گرووپ",
                                             url="https://t.me/joinchannel1bot?startgroup=true")
        markup.add(add_bot)
        bot.send_message(message.chat.id,
                         "👋 سڵاو، بەخێرهاتی بۆ بۆتی JOIN L7N 💙\n"
                         "ئەم بۆتە بۆ پاراستن و پەیوەستکردنی گرووپ و کەناڵ دروست کراوە.\n"
                         "👇 کلیک بکە بۆ زیادکردنی بۆت بۆ گرووپ 👇",
                         reply_markup=markup)

# 📍 فرمانی on بۆ ئەدمین
@bot.message_handler(func=lambda msg: msg.text and msg.text.lower() == "on")
def on_command(message):
    if message.chat.type not in ["group", "supergroup"]:
        return

    member = bot.get_chat_member(message.chat.id, message.from_user.id)
    if member.status not in ["administrator", "creator"]:
        bot.reply_to(message, "⛔ تەنها ئەدمین دەتوانێ ئەم فرمانە بنێرێت.")
        return

    markup = types.InlineKeyboardMarkup()
    ch1 = types.InlineKeyboardButton("➕ زیادکردنی کەناڵ 1", callback_data="add_ch1")
    ch2 = types.InlineKeyboardButton("➕ زیادکردنی کەناڵ 2", callback_data="add_ch2")
    markup.add(ch1, ch2)

    bot.send_message(
        message.chat.id,
        f"👋 سڵاو {message.from_user.first_name}\n"
        f"بۆ زیادکردنی کەناڵەکەت، کلیک بکە لە یەکێ لە دوگمەکان خوارەوە 👇",
        reply_markup=markup
    )

# پەیامی L7N - دوگمەکانی سەرەکی
@bot.message_handler(commands=['L7N'])
def l7n_panel(message):
    markup = types.InlineKeyboardMarkup(row_width=1)
    btn1 = types.InlineKeyboardButton("📝 گۆڕینی ناوی گرووپ", callback_data="change_name")
    btn2 = types.InlineKeyboardButton("🖼 گۆڕینی وێنەی گرووپ", callback_data="change_photo")
    btn3 = types.InlineKeyboardButton("📄 گۆڕینی بایۆی گرووپ", callback_data="change_bio")
    btn4 = types.InlineKeyboardButton("♻️ زفرینا دەسپێکی", callback_data="reset_panel")
    markup.add(btn1, btn2, btn3, btn4)

    bot.send_message(message.chat.id,
                     "⚙️ پەڕەی یارمەتیدانی گرووپ — L7N BOT\n\n"
                     "دوگمەیەک هەڵبژێرە بۆ گۆڕینی تشتەکان👇",
                     reply_markup=markup)

# فەرمانی /L7N بۆ نیشاندانی پەیامە سەرەکی
@bot.message_handler(commands=['L7N'])
def l7n_panel(message):
    markup = types.InlineKeyboardMarkup(row_width=1)
    btn1 = types.InlineKeyboardButton("📝 گۆڕینی ناوی گرووپ", callback_data="change_name")
    btn2 = types.InlineKeyboardButton("🖼 گۆڕینی وێنەی گرووپ", callback_data="change_photo")
    btn3 = types.InlineKeyboardButton("📄 گۆڕینی بایۆی گرووپ", callback_data="change_bio")
    markup.add(btn1, btn2, btn3)
    bot.send_message(message.chat.id,
                     "⚙️ پەڕەی ئەدمین — L7N BOT\n"
                     "دوگمەیەک هەڵبژێرە بۆ گۆڕینی تشتەکان 👇",
                     reply_markup=markup)

# 📩 گەڕانەوەی وەڵامەکان
@bot.callback_query_handler(func=lambda call: True)
def handle_callback(call):
    chat_id = call.message.chat.id
    data = call.data
    bot.answer_callback_query(call.id)

    if data == "change_name":
        bot.send_message(chat_id, "📝 نێوی نوێی گرووپ بنوسە:")
        bot.register_next_step_handler(call.message, change_group_name)
    elif data == "change_photo":
        bot.send_message(chat_id, "🖼 وێنەی نوێی گرووپ بنێرە:")
        bot.register_next_step_handler(call.message, change_group_photo)
    elif data == "change_bio":
        bot.send_message(chat_id, "📄 بایۆی نوێی گرووپ بنوسە:")
        bot.register_next_step_handler(call.message, change_group_bio)


# 🧩 گۆڕینی ناوی گرووپ
def change_group_name(message):
    try:
        new_name = message.text
        bot.set_chat_title(message.chat.id, new_name)
        bot.send_message(message.chat.id, f"✅ ناوی گرووپ نوێ کرایەوە بۆ:\n<b>{new_name}</b>")
    except Exception as e:
        bot.send_message(message.chat.id, f"⚠️ نەتوانرا ناو بگۆڕێت!\n{e}")

# 🧩 گۆڕینی وێنەی گرووپ
def change_group_photo(message):
    try:
        if message.photo:
            file_info = bot.get_file(message.photo[-1].file_id)
            downloaded_file = bot.download_file(file_info.file_path)
            with open("new_photo.jpg", "wb") as new_file:
                new_file.write(downloaded_file)
            with open("new_photo.jpg", "rb") as new_file:
                bot.set_chat_photo(message.chat.id, new_file)
            bot.send_message(message.chat.id, "✅ وێنەی گرووپ نوێ کرایەوە!")
        else:
            bot.send_message(message.chat.id, "⚠️ تکایە وێنە بنێرە.")
    except Exception as e:
        bot.send_message(message.chat.id, f"❌ هەڵەیەک ڕویدا:\n{e}")

# 🧩 گۆڕینی بایۆی گرووپ
def change_group_bio(message):
    try:
        new_bio = message.text
        bot.set_chat_description(message.chat.id, new_bio)
        bot.send_message(message.chat.id, f"✅ بایۆی گرووپ نوێ کرایەوە:\n<blockquote>{new_bio}</blockquote>")
    except Exception as e:
        bot.send_message(message.chat.id, f"⚠️ نەتوانرا بایۆ بگۆڕێت!\n{e}")

# 📍 زیادکردنی کەناڵ 1
@bot.callback_query_handler(func=lambda call: call.data == "add_ch1")
def add_channel_1(call):
    bot.answer_callback_query(call.id)
    bot.send_message(
        call.message.chat.id,
        "📝 تکایە ناوی کەناڵە بنوسە بە شێوەی @examplechannel\n\n🔹 ئەمە بۆ کەناڵی 1 ـە"
    )
    bot.register_next_step_handler(call.message, lambda msg: save_channel_name(msg, 1))

# 📍 زفرینا دەسپێکی (Restart Panel)
@bot.callback_query_handler(func=lambda call: call.data == "reset_panel")
def reset_admin_panel(call):
    chat_id = call.message.chat.id
    bot.delete_message(chat_id, call.message.message_id)
    bot.send_message(chat_id, "🔄 پەیامی سەرەکی نوێ کرایەوە...")
    admin_panel(call.message)

# 📍 زیادکردنی کەناڵ 2
@bot.callback_query_handler(func=lambda call: call.data == "add_ch2")
def add_channel_2(call):
    bot.answer_callback_query(call.id)
    bot.send_message(
        call.message.chat.id,
        "📝 تکایە ناوی کەناڵە بنوسە بە شێوەی @examplechannel\n\n🔹 ئەمە بۆ کەناڵی 2 ـە"
    )
    bot.register_next_step_handler(call.message, lambda msg: save_channel_name(msg, 2))


# ✅ پاشەکەوتکردنی ناوی کەناڵ
def save_channel_name(message, channel_number):
    channel = message.text.strip()

    if not channel.startswith("@"):
        bot.send_message(
            message.chat.id,
            "⚠️ تکایە بە @ دەست پێبکە بەم شێوەیە:\n@examplechannel"
        )
        bot.register_next_step_handler(message, lambda msg: save_channel_name(msg, channel_number))
        return

    try:
        chat_info = bot.get_chat(channel)
        if chat_info.type != "channel":
            raise Exception("not a channel")
    except Exception:
        bot.send_message(
            message.chat.id,
            "❌ ناتوانم ئەو کەناڵە بدۆزمەوە، دڵنیابە ناوەکە دروستە."
        )
        bot.register_next_step_handler(message, lambda msg: save_channel_name(msg, channel_number))
        return

    if message.chat.id not in group_channels:
        group_channels[message.chat.id] = {}

    group_channels[message.chat.id][f"channel_{channel_number}"] = channel

    bot.send_message(
        message.chat.id,
        f"✅ کەناڵی {channel_number} پەیوەست کرا: {channel}"
    )

# 📍 فرمانی off بۆ ئەدمین
@bot.message_handler(func=lambda msg: msg.text and msg.text.lower() == "off")
def off_command(message):
    if message.chat.type not in ["group", "supergroup"]:
        return

    member = bot.get_chat_member(message.chat.id, message.from_user.id)
    if member.status not in ["administrator", "creator"]:
        bot.reply_to(message, "⛔ تەنها ئەدمین دەتوانێ ئەم فرمانە بنێرێت.")
        return

    if message.chat.id in group_channels:
        del group_channels[message.chat.id]
        bot.send_message(
            message.chat.id,
            "⚠️ هەموو کەناڵە پەیوەستەکان هەڵوەشاوە.\n"
            "🚫 بۆتی چێککردنی جوین لەسەر ئەم گرووپە ناچالاک کرا."
        )
    else:
        bot.send_message(
            message.chat.id,
            "ℹ️ بۆت هیچ کەناڵێک پەیوەست نەکردووە پێشتر."
        )

@bot.message_handler(content_types=['new_chat_members'])
def check_join(message):
    chat_id = message.chat.id
    if chat_id not in group_channels:
        return

    for member in message.new_chat_members:
        user_id = member.id
        username = f"@{member.username}" if member.username else member.first_name

        # ئەم بەشە دەتاقیکاتەوە کە ئەیا ئەندامەکە جوینە لە کەناڵەکان یان نا
        for key, channel_username in group_channels[chat_id].items():
            try:
                chat_member = bot.get_chat_member(channel_username, user_id)
                if chat_member.status not in ["member", "administrator", "creator"]:
                    raise Exception("not joined")
            except:
                # ئەگەر ئەدمین بوو، پەیام نەبەخە
                member_status = bot.get_chat_member(chat_id, user_id).status
                if member_status in ["administrator", "creator"]:
                    continue

                # 🔥 پەیامی جوین بکە و دوگمە زیاد بکە
                markup = types.InlineKeyboardMarkup()
                join_btn = types.InlineKeyboardButton(
                    f"📢 کلیک بکە بۆ جوین کردنی {channel_username}",
                    url=f"https://t.me/{channel_username[1:]}"
                )
                markup.add(join_btn)

                sent_msg = bot.send_message(
                    chat_id,
                    f"⚠️ {username}\n"
                    f"پێویستە ئەو کەناڵە جوین بکە پێش ئەوەی بتوانیت چات بکەیت.",
                    reply_markup=markup
                )

                # 🕓 30 چرکە پاشان ئەگەر جوین نەکرد، پەیامەکە بسڕەوە
                import time
                time.sleep(30)

                try:
                    chat_member_check = bot.get_chat_member(channel_username, user_id)
                    if chat_member_check.status not in ["member", "administrator", "creator"]:
                        bot.delete_message(chat_id, sent_msg.message_id)
                        bot.send_message(
                            chat_id,
                            f"🚫 {username} چونە دەرەوە چونکە جوین نەکرد بۆ {channel_username}."
                        )
                except:
                    pass

# 📍 ئەگەر کەسێک پەیام بنێرێت و نەبووە جوین → پەیامەکە بسڕەوە و ئاگادار بکە
@bot.message_handler(func=lambda m: m.chat.type in ["group", "supergroup"])
def delete_non_joined(message):
    chat_id = message.chat.id
    user_id = message.from_user.id
    username = f"@{message.from_user.username}" if message.from_user.username else message.from_user.first_name

    # ئەگەر بۆت نەبووە پەیوەست کراو بۆ ئەم گرووپە
    if chat_id not in group_channels:
        return

    # ئەدمینەکان تێدەبە
    member_status = bot.get_chat_member(chat_id, user_id).status
    if member_status in ["administrator", "creator"]:
        return

    # چێککردنی ئەیا ئەندامەکە جوینە لە هەموو کەناڵەکان
    for _, channel_username in group_channels[chat_id].items():
        try:
            chat_member = bot.get_chat_member(channel_username, user_id)
            if chat_member.status not in ["member", "administrator", "creator"]:
                raise Exception("not joined")
        except:
            # 🗑️ پەیامی ئەو ئەندامە بسڕەوە
            try:
                bot.delete_message(chat_id, message.message_id)
            except:
                pass

            # 🔔 پەیامی ئاگادارکردن بنێرە
            markup = types.InlineKeyboardMarkup()
            join_btn = types.InlineKeyboardButton(
                f"📢 کلیک بکە بۆ جوین کردنی {channel_username}",
                url=f"https://t.me/{channel_username[1:]}"
            )
            markup.add(join_btn)

            bot.send_message(
                chat_id,
                f"⚠️ {username}\n"
                f"پێویستە سەرەتا جوین بکەیت لە {channel_username} پاشان دەتوانیت چات بکەیت.",
                reply_markup=markup
            )
            return

# 📍 ئەگەر ئەندامەکە پەیوەست نەکراوە → ئاگادار بکە
user_warnings = {}  # بۆ پاراستنی IDی پەیامە ئاگادارکردنەکان

@bot.message_handler(func=lambda m: m.chat.type in ["group", "supergroup"])
def delete_non_joined(message):
    chat_id = message.chat.id
    user_id = message.from_user.id
    username = f"@{message.from_user.username}" if message.from_user.username else message.from_user.first_name

    if chat_id not in group_channels:
        return

    # ئەگەر ئەدمینە، پەیامی نەسڕەوە
    member_status = bot.get_chat_member(chat_id, user_id).status
    if member_status in ["administrator", "creator"]:
        return

    # چێککردنی ئەیا ئەندامەکە جوینە لە کەناڵەکان
    for _, channel_username in group_channels[chat_id].items():
        try:
            chat_member = bot.get_chat_member(channel_username, user_id)
            if chat_member.status not in ["member", "administrator", "creator"]:
                raise Exception("not joined")
        except:
            try:
                bot.delete_message(chat_id, message.message_id)
            except:
                pass

            # ئەگەر پێشتر ئاگادارکراوە، دووبارە نەبەخە
            if user_id in user_warnings:
                return

            # 📩 پەیامی ئاگادارکردن بنێرە
            markup = types.InlineKeyboardMarkup()
            join_btn = types.InlineKeyboardButton(
                f"📢 کلیک بکە بۆ جوین کردنی {channel_username}",
                url=f"https://t.me/{channel_username[1:]}"
            )
            markup.add(join_btn)

            sent_msg = bot.send_message(
                chat_id,
                f"⚠️ {username}\n"
                f"پێویستە سەرەتا جوین بکەیت لە {channel_username} پاشان دەتوانیت چات بکەیت.",
                reply_markup=markup
            )

            # پاراستنی IDی پەیامە ئاگادارکردنە
            user_warnings[user_id] = (chat_id, sent_msg.message_id, channel_username)
            return


# 📍 ئەگەر ئەندامەکە دوای ئەوە جوین بکات → پەیامی ئاگادارکردن بسڕەوە
def check_user_join():
    while True:
        for user_id, (chat_id, warn_msg_id, channel_username) in list(user_warnings.items()):
            try:
                chat_member = bot.get_chat_member(channel_username, user_id)
                if chat_member.status in ["member", "administrator", "creator"]:
                    # 🗑️ ئەگەر جوین کرد → پەیامی ئاگادارکردن بسڕەوە
                    bot.delete_message(chat_id, warn_msg_id)
                    del user_warnings[user_id]
            except:
                pass
        time.sleep(10)  # چێک بکە هەموو 10 چرکە جارێک


# 🔄 بەرەوپێش بردنی چێک‌کردنەکە لە Threadێکی تایبەتی
import threading
threading.Thread(target=check_user_join, daemon=True).start()

# 📍 چێککردنی ئەندامان
@bot.message_handler(content_types=['new_chat_members'])
def check_join(message):
    chat_id = message.chat.id
    if chat_id not in group_channels:
        return

    for member in message.new_chat_members:
        user_id = member.id
        username = f"@{member.username}" if member.username else member.first_name

        for key, channel_username in group_channels[chat_id].items():
            try:
                chat_member = bot.get_chat_member(channel_username, user_id)
                if chat_member.status not in ["member", "administrator", "creator"]:
                    raise Exception("not joined")
            except:
                markup = types.InlineKeyboardMarkup()
                join_btn = types.InlineKeyboardButton(
                    f"📢 کلیک بکە بۆ جوین کردنی {channel_username}",
                    url=f"https://t.me/{channel_username[1:]}"
                )
                markup.add(join_btn)

                bot.send_message(
                    chat_id,
                    f"⚠️ {username}\n"
                    f"بۆ بەشداربوون پێویستە ئەو کەناڵە جوین بکە 👇",reply_markup=markup
                )

print("🤖 بۆت بەسەرکەوتووی چالاکە...")
=======
import telebot
from telebot import types
import time

BOT_TOKEN = "8000635137:AAE9bKrh3e8fdG1OzS0yUkJAhgZwxbZxet0"
bot = telebot.TeleBot(BOT_TOKEN)

# هەر گرووپێک → لیستی کەناڵەکانی خۆی
group_channels = {}

# 🟢 فرمانی start ل پریفات
@bot.message_handler(commands=['start'])
def start_private(message):
    if message.chat.type == "private":
        markup = types.InlineKeyboardMarkup()
        add_bot = types.InlineKeyboardButton("➕ زیادکردنی بۆت بۆ گرووپ",
                                             url="https://t.me/joinchannel1bot?startgroup=true")
        markup.add(add_bot)
        bot.send_message(message.chat.id,
                         "👋 سڵاو، بەخێرهاتی بۆ بۆتی JOIN L7N 💙\n"
                         "ئەم بۆتە بۆ پاراستن و پەیوەستکردنی گرووپ و کەناڵ دروست کراوە.\n"
                         "👇 کلیک بکە بۆ زیادکردنی بۆت بۆ گرووپ 👇",
                         reply_markup=markup)

# 📍 فرمانی on بۆ ئەدمین
@bot.message_handler(func=lambda msg: msg.text and msg.text.lower() == "on")
def on_command(message):
    if message.chat.type not in ["group", "supergroup"]:
        return

    member = bot.get_chat_member(message.chat.id, message.from_user.id)
    if member.status not in ["administrator", "creator"]:
        bot.reply_to(message, "⛔ تەنها ئەدمین دەتوانێ ئەم فرمانە بنێرێت.")
        return

    markup = types.InlineKeyboardMarkup()
    ch1 = types.InlineKeyboardButton("➕ زیادکردنی کەناڵ 1", callback_data="add_ch1")
    ch2 = types.InlineKeyboardButton("➕ زیادکردنی کەناڵ 2", callback_data="add_ch2")
    markup.add(ch1, ch2)

    bot.send_message(
        message.chat.id,
        f"👋 سڵاو {message.from_user.first_name}\n"
        f"بۆ زیادکردنی کەناڵەکەت، کلیک بکە لە یەکێ لە دوگمەکان خوارەوە 👇",
        reply_markup=markup
    )

# پەیامی L7N - دوگمەکانی سەرەکی
@bot.message_handler(commands=['L7N'])
def l7n_panel(message):
    markup = types.InlineKeyboardMarkup(row_width=1)
    btn1 = types.InlineKeyboardButton("📝 گۆڕینی ناوی گرووپ", callback_data="change_name")
    btn2 = types.InlineKeyboardButton("🖼 گۆڕینی وێنەی گرووپ", callback_data="change_photo")
    btn3 = types.InlineKeyboardButton("📄 گۆڕینی بایۆی گرووپ", callback_data="change_bio")
    btn4 = types.InlineKeyboardButton("♻️ زفرینا دەسپێکی", callback_data="reset_panel")
    markup.add(btn1, btn2, btn3, btn4)

    bot.send_message(message.chat.id,
                     "⚙️ پەڕەی یارمەتیدانی گرووپ — L7N BOT\n\n"
                     "دوگمەیەک هەڵبژێرە بۆ گۆڕینی تشتەکان👇",
                     reply_markup=markup)

# فەرمانی /L7N بۆ نیشاندانی پەیامە سەرەکی
@bot.message_handler(commands=['L7N'])
def l7n_panel(message):
    markup = types.InlineKeyboardMarkup(row_width=1)
    btn1 = types.InlineKeyboardButton("📝 گۆڕینی ناوی گرووپ", callback_data="change_name")
    btn2 = types.InlineKeyboardButton("🖼 گۆڕینی وێنەی گرووپ", callback_data="change_photo")
    btn3 = types.InlineKeyboardButton("📄 گۆڕینی بایۆی گرووپ", callback_data="change_bio")
    markup.add(btn1, btn2, btn3)
    bot.send_message(message.chat.id,
                     "⚙️ پەڕەی ئەدمین — L7N BOT\n"
                     "دوگمەیەک هەڵبژێرە بۆ گۆڕینی تشتەکان 👇",
                     reply_markup=markup)

# 📩 گەڕانەوەی وەڵامەکان
@bot.callback_query_handler(func=lambda call: True)
def handle_callback(call):
    chat_id = call.message.chat.id
    data = call.data
    bot.answer_callback_query(call.id)

    if data == "change_name":
        bot.send_message(chat_id, "📝 نێوی نوێی گرووپ بنوسە:")
        bot.register_next_step_handler(call.message, change_group_name)
    elif data == "change_photo":
        bot.send_message(chat_id, "🖼 وێنەی نوێی گرووپ بنێرە:")
        bot.register_next_step_handler(call.message, change_group_photo)
    elif data == "change_bio":
        bot.send_message(chat_id, "📄 بایۆی نوێی گرووپ بنوسە:")
        bot.register_next_step_handler(call.message, change_group_bio)


# 🧩 گۆڕینی ناوی گرووپ
def change_group_name(message):
    try:
        new_name = message.text
        bot.set_chat_title(message.chat.id, new_name)
        bot.send_message(message.chat.id, f"✅ ناوی گرووپ نوێ کرایەوە بۆ:\n<b>{new_name}</b>")
    except Exception as e:
        bot.send_message(message.chat.id, f"⚠️ نەتوانرا ناو بگۆڕێت!\n{e}")

# 🧩 گۆڕینی وێنەی گرووپ
def change_group_photo(message):
    try:
        if message.photo:
            file_info = bot.get_file(message.photo[-1].file_id)
            downloaded_file = bot.download_file(file_info.file_path)
            with open("new_photo.jpg", "wb") as new_file:
                new_file.write(downloaded_file)
            with open("new_photo.jpg", "rb") as new_file:
                bot.set_chat_photo(message.chat.id, new_file)
            bot.send_message(message.chat.id, "✅ وێنەی گرووپ نوێ کرایەوە!")
        else:
            bot.send_message(message.chat.id, "⚠️ تکایە وێنە بنێرە.")
    except Exception as e:
        bot.send_message(message.chat.id, f"❌ هەڵەیەک ڕویدا:\n{e}")

# 🧩 گۆڕینی بایۆی گرووپ
def change_group_bio(message):
    try:
        new_bio = message.text
        bot.set_chat_description(message.chat.id, new_bio)
        bot.send_message(message.chat.id, f"✅ بایۆی گرووپ نوێ کرایەوە:\n<blockquote>{new_bio}</blockquote>")
    except Exception as e:
        bot.send_message(message.chat.id, f"⚠️ نەتوانرا بایۆ بگۆڕێت!\n{e}")

# 📍 زیادکردنی کەناڵ 1
@bot.callback_query_handler(func=lambda call: call.data == "add_ch1")
def add_channel_1(call):
    bot.answer_callback_query(call.id)
    bot.send_message(
        call.message.chat.id,
        "📝 تکایە ناوی کەناڵە بنوسە بە شێوەی @examplechannel\n\n🔹 ئەمە بۆ کەناڵی 1 ـە"
    )
    bot.register_next_step_handler(call.message, lambda msg: save_channel_name(msg, 1))

# 📍 زفرینا دەسپێکی (Restart Panel)
@bot.callback_query_handler(func=lambda call: call.data == "reset_panel")
def reset_admin_panel(call):
    chat_id = call.message.chat.id
    bot.delete_message(chat_id, call.message.message_id)
    bot.send_message(chat_id, "🔄 پەیامی سەرەکی نوێ کرایەوە...")
    admin_panel(call.message)

# 📍 زیادکردنی کەناڵ 2
@bot.callback_query_handler(func=lambda call: call.data == "add_ch2")
def add_channel_2(call):
    bot.answer_callback_query(call.id)
    bot.send_message(
        call.message.chat.id,
        "📝 تکایە ناوی کەناڵە بنوسە بە شێوەی @examplechannel\n\n🔹 ئەمە بۆ کەناڵی 2 ـە"
    )
    bot.register_next_step_handler(call.message, lambda msg: save_channel_name(msg, 2))


# ✅ پاشەکەوتکردنی ناوی کەناڵ
def save_channel_name(message, channel_number):
    channel = message.text.strip()

    if not channel.startswith("@"):
        bot.send_message(
            message.chat.id,
            "⚠️ تکایە بە @ دەست پێبکە بەم شێوەیە:\n@examplechannel"
        )
        bot.register_next_step_handler(message, lambda msg: save_channel_name(msg, channel_number))
        return

    try:
        chat_info = bot.get_chat(channel)
        if chat_info.type != "channel":
            raise Exception("not a channel")
    except Exception:
        bot.send_message(
            message.chat.id,
            "❌ ناتوانم ئەو کەناڵە بدۆزمەوە، دڵنیابە ناوەکە دروستە."
        )
        bot.register_next_step_handler(message, lambda msg: save_channel_name(msg, channel_number))
        return

    if message.chat.id not in group_channels:
        group_channels[message.chat.id] = {}

    group_channels[message.chat.id][f"channel_{channel_number}"] = channel

    bot.send_message(
        message.chat.id,
        f"✅ کەناڵی {channel_number} پەیوەست کرا: {channel}"
    )

# 📍 فرمانی off بۆ ئەدمین
@bot.message_handler(func=lambda msg: msg.text and msg.text.lower() == "off")
def off_command(message):
    if message.chat.type not in ["group", "supergroup"]:
        return

    member = bot.get_chat_member(message.chat.id, message.from_user.id)
    if member.status not in ["administrator", "creator"]:
        bot.reply_to(message, "⛔ تەنها ئەدمین دەتوانێ ئەم فرمانە بنێرێت.")
        return

    if message.chat.id in group_channels:
        del group_channels[message.chat.id]
        bot.send_message(
            message.chat.id,
            "⚠️ هەموو کەناڵە پەیوەستەکان هەڵوەشاوە.\n"
            "🚫 بۆتی چێککردنی جوین لەسەر ئەم گرووپە ناچالاک کرا."
        )
    else:
        bot.send_message(
            message.chat.id,
            "ℹ️ بۆت هیچ کەناڵێک پەیوەست نەکردووە پێشتر."
        )

@bot.message_handler(content_types=['new_chat_members'])
def check_join(message):
    chat_id = message.chat.id
    if chat_id not in group_channels:
        return

    for member in message.new_chat_members:
        user_id = member.id
        username = f"@{member.username}" if member.username else member.first_name

        # ئەم بەشە دەتاقیکاتەوە کە ئەیا ئەندامەکە جوینە لە کەناڵەکان یان نا
        for key, channel_username in group_channels[chat_id].items():
            try:
                chat_member = bot.get_chat_member(channel_username, user_id)
                if chat_member.status not in ["member", "administrator", "creator"]:
                    raise Exception("not joined")
            except:
                # ئەگەر ئەدمین بوو، پەیام نەبەخە
                member_status = bot.get_chat_member(chat_id, user_id).status
                if member_status in ["administrator", "creator"]:
                    continue

                # 🔥 پەیامی جوین بکە و دوگمە زیاد بکە
                markup = types.InlineKeyboardMarkup()
                join_btn = types.InlineKeyboardButton(
                    f"📢 کلیک بکە بۆ جوین کردنی {channel_username}",
                    url=f"https://t.me/{channel_username[1:]}"
                )
                markup.add(join_btn)

                sent_msg = bot.send_message(
                    chat_id,
                    f"⚠️ {username}\n"
                    f"پێویستە ئەو کەناڵە جوین بکە پێش ئەوەی بتوانیت چات بکەیت.",
                    reply_markup=markup
                )

                # 🕓 30 چرکە پاشان ئەگەر جوین نەکرد، پەیامەکە بسڕەوە
                import time
                time.sleep(30)

                try:
                    chat_member_check = bot.get_chat_member(channel_username, user_id)
                    if chat_member_check.status not in ["member", "administrator", "creator"]:
                        bot.delete_message(chat_id, sent_msg.message_id)
                        bot.send_message(
                            chat_id,
                            f"🚫 {username} چونە دەرەوە چونکە جوین نەکرد بۆ {channel_username}."
                        )
                except:
                    pass

# 📍 ئەگەر کەسێک پەیام بنێرێت و نەبووە جوین → پەیامەکە بسڕەوە و ئاگادار بکە
@bot.message_handler(func=lambda m: m.chat.type in ["group", "supergroup"])
def delete_non_joined(message):
    chat_id = message.chat.id
    user_id = message.from_user.id
    username = f"@{message.from_user.username}" if message.from_user.username else message.from_user.first_name

    # ئەگەر بۆت نەبووە پەیوەست کراو بۆ ئەم گرووپە
    if chat_id not in group_channels:
        return

    # ئەدمینەکان تێدەبە
    member_status = bot.get_chat_member(chat_id, user_id).status
    if member_status in ["administrator", "creator"]:
        return

    # چێککردنی ئەیا ئەندامەکە جوینە لە هەموو کەناڵەکان
    for _, channel_username in group_channels[chat_id].items():
        try:
            chat_member = bot.get_chat_member(channel_username, user_id)
            if chat_member.status not in ["member", "administrator", "creator"]:
                raise Exception("not joined")
        except:
            # 🗑️ پەیامی ئەو ئەندامە بسڕەوە
            try:
                bot.delete_message(chat_id, message.message_id)
            except:
                pass

            # 🔔 پەیامی ئاگادارکردن بنێرە
            markup = types.InlineKeyboardMarkup()
            join_btn = types.InlineKeyboardButton(
                f"📢 کلیک بکە بۆ جوین کردنی {channel_username}",
                url=f"https://t.me/{channel_username[1:]}"
            )
            markup.add(join_btn)

            bot.send_message(
                chat_id,
                f"⚠️ {username}\n"
                f"پێویستە سەرەتا جوین بکەیت لە {channel_username} پاشان دەتوانیت چات بکەیت.",
                reply_markup=markup
            )
            return

# 📍 ئەگەر ئەندامەکە پەیوەست نەکراوە → ئاگادار بکە
user_warnings = {}  # بۆ پاراستنی IDی پەیامە ئاگادارکردنەکان

@bot.message_handler(func=lambda m: m.chat.type in ["group", "supergroup"])
def delete_non_joined(message):
    chat_id = message.chat.id
    user_id = message.from_user.id
    username = f"@{message.from_user.username}" if message.from_user.username else message.from_user.first_name

    if chat_id not in group_channels:
        return

    # ئەگەر ئەدمینە، پەیامی نەسڕەوە
    member_status = bot.get_chat_member(chat_id, user_id).status
    if member_status in ["administrator", "creator"]:
        return

    # چێککردنی ئەیا ئەندامەکە جوینە لە کەناڵەکان
    for _, channel_username in group_channels[chat_id].items():
        try:
            chat_member = bot.get_chat_member(channel_username, user_id)
            if chat_member.status not in ["member", "administrator", "creator"]:
                raise Exception("not joined")
        except:
            try:
                bot.delete_message(chat_id, message.message_id)
            except:
                pass

            # ئەگەر پێشتر ئاگادارکراوە، دووبارە نەبەخە
            if user_id in user_warnings:
                return

            # 📩 پەیامی ئاگادارکردن بنێرە
            markup = types.InlineKeyboardMarkup()
            join_btn = types.InlineKeyboardButton(
                f"📢 کلیک بکە بۆ جوین کردنی {channel_username}",
                url=f"https://t.me/{channel_username[1:]}"
            )
            markup.add(join_btn)

            sent_msg = bot.send_message(
                chat_id,
                f"⚠️ {username}\n"
                f"پێویستە سەرەتا جوین بکەیت لە {channel_username} پاشان دەتوانیت چات بکەیت.",
                reply_markup=markup
            )

            # پاراستنی IDی پەیامە ئاگادارکردنە
            user_warnings[user_id] = (chat_id, sent_msg.message_id, channel_username)
            return


# 📍 ئەگەر ئەندامەکە دوای ئەوە جوین بکات → پەیامی ئاگادارکردن بسڕەوە
def check_user_join():
    while True:
        for user_id, (chat_id, warn_msg_id, channel_username) in list(user_warnings.items()):
            try:
                chat_member = bot.get_chat_member(channel_username, user_id)
                if chat_member.status in ["member", "administrator", "creator"]:
                    # 🗑️ ئەگەر جوین کرد → پەیامی ئاگادارکردن بسڕەوە
                    bot.delete_message(chat_id, warn_msg_id)
                    del user_warnings[user_id]
            except:
                pass
        time.sleep(10)  # چێک بکە هەموو 10 چرکە جارێک


# 🔄 بەرەوپێش بردنی چێک‌کردنەکە لە Threadێکی تایبەتی
import threading
threading.Thread(target=check_user_join, daemon=True).start()

# 📍 چێککردنی ئەندامان
@bot.message_handler(content_types=['new_chat_members'])
def check_join(message):
    chat_id = message.chat.id
    if chat_id not in group_channels:
        return

    for member in message.new_chat_members:
        user_id = member.id
        username = f"@{member.username}" if member.username else member.first_name

        for key, channel_username in group_channels[chat_id].items():
            try:
                chat_member = bot.get_chat_member(channel_username, user_id)
                if chat_member.status not in ["member", "administrator", "creator"]:
                    raise Exception("not joined")
            except:
                markup = types.InlineKeyboardMarkup()
                join_btn = types.InlineKeyboardButton(
                    f"📢 کلیک بکە بۆ جوین کردنی {channel_username}",
                    url=f"https://t.me/{channel_username[1:]}"
                )
                markup.add(join_btn)

                bot.send_message(
                    chat_id,
                    f"⚠️ {username}\n"
                    f"بۆ بەشداربوون پێویستە ئەو کەناڵە جوین بکە 👇",reply_markup=markup
                )

print("🤖 بۆت بەسەرکەوتووی چالاکە...")
>>>>>>> 5c2ae79dd32e583402aed64fffcba64a6d8c2082
bot.infinity_polling()