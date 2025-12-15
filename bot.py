import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

TOKEN = os.getenv("TOKEN")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("🔍 BIN 查询", callback_data="bin")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("请选择功能：", reply_markup=reply_markup)

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "bin":
        await query.edit_message_text("请输入 BIN（前 6 位卡号）")

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    if text.isdigit() and len(text) >= 6:
        await update.message.reply_text(f"你输入的 BIN 是：{text[:6]}")
    else:
        await update.message.reply_text("请输入正确的 BIN（至少 6 位数字）")

def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))

    print("Bot started")  # 让 Logs 一定有内容
    app.run_polling()

if __name__ == "__main__":
    main()
