
import os
import telegram

BOT_TOKEN = os.environ.get("BOT_TOKEN")

bot = telegram.Bot(token=BOT_TOKEN)

# Отримуємо останні повідомлення, щоб витягнути chat_id
updates = bot.get_updates()

if not updates:
    print("❌ Немає повідомлень. Напиши щось боту в Telegram!")
else:
    for update in updates:
        chat = update.message.chat
        print(f"✅ CHAT_ID: {chat.id}")
        print(f"👤 Username: @{chat.username}")
