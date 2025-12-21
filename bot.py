import requests
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
import os

BOT_TOKEN = os.getenv("8346855772:AAE9KiNbgn70dclW_m-fBAlEEqtra4zqSxE")

def query_bin(bin_number: str):
    url = f"https://lookup.binlist.net/{bin_number}"
    try:
        r = requests.get(url, timeout=10)
        if r.status_code != 200:
            return f"〔🌱〕 BIN ➤ {bin_number}\n❌ 查询失败\n"

        data = r.json()
        return (
            f"〔🌱〕 BIN ➤ {bin_number}\n"
            f"〔💳〕 Card Brand ➤ {data.get('scheme', '未知')}\n"
            f"〔💰〕 Card Type ➤ {data.get('type', '未知')}\n"
            f"〔🏆〕 Card Level ➤ {data.get('brand', '未知')}\n"
            f"〔🏦〕 Bank Name ➤ {data.get('bank', {}).get('name', '未知')}\n"
            f"〔🌍〕 Country ➤ {data.get('country', {}).get('name', '未知')} {data.get('country', {}).get('emoji', '')}\n"
        )
    except Exception:
        return f"〔🌱〕 BIN ➤ {bin_number}\n❌ 查询异常\n"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [["开始查询 BIN"]]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    await update.message.reply_text(
        "👋 欢迎使用 BIN 查询机器人\n\n"
        "📌 直接发送 6 位 BIN\n"
        "📌 可一次发送多个（空格 / 换行分隔）",
        reply_markup=reply_markup
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    bins = [x for x in text.replace("\n", " ").split(" ") if x.isdigit() and len(x) == 6]

    if not bins:
        await update.message.reply_text("❗请输入 6 位 BIN，可多个")
        return

    result = ""
    for b in bins:
        result += query_bin(b) + "\n"

    await update.message.reply_text(result)

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.run_polling()

if __name__ == "__main__":
    main()
