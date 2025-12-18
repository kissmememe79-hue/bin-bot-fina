import os
import re
import requests
from dotenv import load_dotenv

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters,
)

# 读取环境变量
load_dotenv()
TOKEN = os.getenv("TOKEN")

# ================= BIN 查询函数 =================
def query_bin(bin_code: str):
    url = f"https://lookup.binlist.net/{bin_code}"
    r = requests.get(url, timeout=10)

    if r.status_code != 200:
        return None

    data = r.json()

    return {
        "bin": bin_code,
        "brand": data.get("scheme", "未知").upper(),
        "type": data.get("type", "未知"),
        "level": data.get("brand", "未知"),
        "bank": data.get("bank", {}).get("name", "未知"),
        "country": data.get("country", {}).get("name", "未知"),
    }


# ================= /start =================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("🔍 开始 BIN 查询", callback_data="start_query")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        "🤖 BIN 查询机器人\n\n"
        "👉 点击下方按钮\n"
        "👉 直接发送【前6位或多个 BIN】即可查询\n\n"
        "示例：\n"
        "457173\n"
        "457173 520082 433666",
        reply_markup=reply_markup
    )


# ================= 菜单按钮 =================
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "start_query":
        await query.message.reply_text(
            "请输入 BIN（前6位）\n"
            "支持多个，用空格或换行分开"
        )


# ================= 处理 BIN 输入 =================
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    bins = re.findall(r"\b\d{6}\b", text)

    if not bins:
        await update.message.reply_text("❌ 未检测到有效 BIN（需 6 位数字）")
        return

    results = []

    for b in bins:
        info = query_bin(b)
        if not info:
            results.append(f"【{b}】查询失败")
            continue

        msg = (
            f"〔🌱〕 BIN ➤ {info['bin']}\n"
            f"〔💳〕 Card Brand ➤ {info['brand']}（卡组织）\n"
            f"〔💰〕 Card Type ➤ {info['type']}（卡类型）\n"
            f"〔🏆〕 Card Level ➤ {info['level']}（卡级别）\n"
            f"〔🏦〕 Bank Name ➤ {info['bank']}（银行）\n"
            f"〔🌍〕 Country ➤ {info['country']}（国家）\n"
            "——————————————"
        )
        results.append(msg)

    await update.message.reply_text("\n".join(results))


# ================= 主入口 =================
def main():
    if not TOKEN:
        raise RuntimeError("TOKEN 未设置，请在 Railway 中添加 TOKEN")

    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("✅ BIN 查询机器人已启动（24h）")
    app.run_polling()


if __name__ == "__main__":
    main()
