import asyncio
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
from openai import OpenAI

# --- OpenRouter настройка ---
client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key="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",
)

# --- фикс event loop для Python 3.11+ ---
try:
    asyncio.get_running_loop()
except RuntimeError:
    asyncio.set_event_loop(asyncio.new_event_loop())
# ----------------------------------------

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Привет! Я умный бот 🤖. Напиши мне что-нибудь!")

async def clear(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.chat_data.clear()
    await update.message.reply_text("🧹 История очищена!")

async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text
    context.chat_data.setdefault("history", [])
    context.chat_data["history"].append({"role": "user", "content": user_message})

    try:
        response = client.chat.completions.create(
            model="mistralai/mixtral-8x7b-instruct",  # ✅ правильное имя
            messages=[
                {"role": "system", "content": "Ты дружелюбный Telegram-бот."},
                *context.chat_data["history"],
            ],
        )

        reply = response.choices[0].message.content  # ✅ теперь это объект, а не строка

        context.chat_data["history"].append({"role": "assistant", "content": reply})
        await update.message.reply_text(reply)

    except Exception as e:
        await update.message.reply_text(f"⚠️ Ошибка: {e}")

def main():
    app = ApplicationBuilder().token("8310118295:AAFpnMbnXc68_EfZI2H-eibThMmxQsg_2Bg").build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("clear", clear))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message_handler))

    print("✅ Бот запущен!")
    app.run_polling()

if __name__ == "__main__":
    main()
