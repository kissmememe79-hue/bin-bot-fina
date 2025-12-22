import os
import requests
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

# ====== 必须的环境变量检查 ======
BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise RuntimeError("BOT_TOKEN is missing or empty")

# ====== 中文映射 ======
CARD_TYPE_MAP = {
    "credit": "信用卡",
    "debit": "借记卡",
    "prepaid": "预付卡",
}

CARD_LEVEL_MAP = {
    "classic": "普通卡",
    "standard": "标准卡",
    "gold": "金卡",
    "platinum": "白金卡",
    "world": "世界卡",
    "world elite": "世界精英卡",
    "infinite": "无限卡",
    "signature": "签名卡",
}

BRAND_MAP = {
    "visa": "VISA",
    "mastercard": "MasterCard",
    "amex": "American Express",
    "discover": "Discover",
    "jcb": "JCB",
    "unionpay": "银联",
}

# ====== 查询 BIN ======
def query_bin(bin_code: str) -> str:
    try:
        r = requests.get(f"https://lookup.binlist.net/{bin_code}", timeout=10)
        if r.status_code != 200:
            return f"〔🌱〕 BIN ➤ {bin_code}\n❌ 查询失败"

        data = r.json()

        brand = BRAND_MAP.get(data.get("scheme", ""), data.get("scheme", "未知"))
        card_type = CARD_TYPE_MAP.get(data.get("type", ""), data.get("type", "未知"))
        level = CARD_LEVEL_MAP.get(data.get("brand", "").lower(), data.get("brand", "未知"))

        bank = data.get("bank", {}).get("name", "未知")
        country = data.get("country", {}).get("name", "未知")
        emoji = data.get("country", {}).get("emoji", "")

        return (
            f"〔🌱〕 BIN ➤ {bin_code}\n"
            f"〔💳〕 Card Brand ➤ {brand}\n"
            f"〔💰〕 Card Type ➤ {card_type}\n"
            f"〔🏆〕 Card Level ➤ {level}\n"
            f"〔🏦〕 Bank Name ➤ {bank}\n"
            f"〔🌍〕 Country ➤ {country} {emoji}"
        )
    except Exception as e:
        return f"〔🌱〕 BIN ➤ {bin_code}\n❌ 查询异常"

# ====== /start ======
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🤖 BIN 查询机器人\n\n"
        "📌 使用方法：\n"
        "直接发送 BIN 号码即可（支持多个）\n\n"
        "示例：\n"
        "519311\n"
        "或：\n"
        "519311 457173\n\n"
        "🌐 24 小时在线 · 免费使用"
    )

# ====== 处理消息 ======
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    bins = [b for b in text.replace("\n", " ").split(" ") if b.isdigit() and 6 <= len(b) <= 8]

    if not bins:
        await update.message.reply_text("❗请输入正确的 BIN（6-8 位数字）")
        return

    results = []
    for b in bins:
        results.append(query_bin(b))

    await update.message.reply_text("\n\n".join(results))

# ====== 启动 ======
def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("BIN Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
