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

# ===== 必须的环境变量 =====
BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise RuntimeError("BOT_TOKEN is missing or empty")

# ===== 中文映射 =====
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
    "signature": "签名卡",
    "infinite": "无限卡",
}

CARD_BRAND_MAP = {
    "visa": "VISA",
    "mastercard": "万事达",
    "amex": "美国运通",
    "discover": "Discover",
    "jcb": "JCB",
    "unionpay": "银联",
}

# ===== BIN 查询 =====
def query_bin(bin_code: str) -> dict:
    url = f"https://lookup.binlist.net/{bin_code}"
    r = requests.get(url, timeout=10)
    r.raise_for_status()
    return r.json()

# ===== /start =====
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 欢迎使用 BIN 查询机器人\n\n"
        "📌 使用方法：\n"
        "直接发送 6 位 BIN，例如：\n"
        "519311\n\n"
        "📊 将自动返回卡片信息（中文）"
    )

# ===== 处理 BIN =====
async def handle_bin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()

    if not text.isdigit() or len(text) != 6:
        await update.message.reply_text("❌ 请输入正确的 6 位 BIN")
        return

    try:
        data = query_bin(text)

        brand_en = data.get("scheme", "")
        type_en = data.get("type", "")
        level_en = data.get("brand", "")

        bank = data.get("bank", {}).get("name", "未知")
        country = data.get("country", {}).get("name", "未知")
        emoji = data.get("country", {}).get("emoji", "")

        msg = (
            f"〔🌱〕 BIN ➤ {text}\n"
            f"〔💳〕 Card Brand ➤ {CARD_BRAND_MAP.get(brand_en, brand_en)}\n"
            f"〔💰〕 Card Type ➤ {CARD_TYPE_MAP.get(type_en, type_en)}\n"
            f"〔🏆〕 Card Level ➤ {CARD_LEVEL_MAP.get(level_en.lower(), level_en)}\n"
            f"〔🏦〕 Bank Name ➤ {bank}\n"
            f"〔🌍〕 Country ➤ {country} {emoji}"
        )

        await update.message.reply_text(msg)

    except Exception as e:
        await update.message.reply_text(f"❌ 查询失败：{e}")

# ===== 启动 =====
def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_bin))

    app.run_polling()

if __name__ == "__main__":
    main()
