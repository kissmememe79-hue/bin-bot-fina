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

# ========= 环境变量 =========
BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise RuntimeError("BOT_TOKEN is missing or empty")

# ========= 中文映射 =========
CARD_BRAND_MAP = {
    "visa": "维萨",
    "mastercard": "万事达",
    "amex": "美国运通",
    "discover": "发现卡",
    "jcb": "JCB",
    "unionpay": "银联",
}

CARD_TYPE_MAP = {
    "credit": "信用卡",
    "debit": "借记卡",
    "prepaid": "预付卡",
}

CARD_LEVEL_MAP = {
    "classic": "普卡",
    "gold": "金卡",
    "platinum": "白金卡",
    "world": "世界卡",
    "signature": "签名卡",
    "infinite": "无限卡",
}

# ========= 查询 BIN =========
def query_bin(bin_code: str) -> str:
    try:
        r = requests.get(f"https://lookup.binlist.net/{bin_code}", timeout=10)
        if r.status_code != 200:
            return f"❌ BIN {bin_code} 查询失败"

        data = r.json()

        brand_raw = (data.get("scheme") or "").lower()
        type_raw = (data.get("type") or "").lower()
        level_raw = (data.get("brand") or "").lower()

        brand = CARD_BRAND_MAP.get(brand_raw, brand_raw or "未知")
        card_type = CARD_TYPE_MAP.get(type_raw, type_raw or "未知")
        level = CARD_LEVEL_MAP.get(level_raw, level_raw or "未知")

        bank = data.get("bank", {}).get("name", "未知")
        
        country_raw = data.get("country", {}).get("name", "")
        country = COUNTRY_MAP.get(country_raw, country_raw or "未知")
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
        return f"❌ BIN {bin_code} 查询异常：{e}"

# ========= /start =========
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 欢迎使用 BIN 查询机器人\n\n"
        "📌 使用方法：\n"
        "• 直接发送 6 位 BIN\n"
        "• 支持一次发送多个（空格或换行分隔）\n\n"
        "示例：\n"
        "519311\n"
        "457173 406173"
    )

# ========= 处理消息 =========
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    bins = [x for x in text.replace("\n", " ").split(" ") if x.isdigit() and len(x) == 6]

    if not bins:
        await update.message.reply_text("❌ 请输入 6 位 BIN 号码")
        return

    results = [query_bin(b) for b in bins]
    await update.message.reply_text("\n\n".join(results))

# ========= 主入口 =========
def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.run_polling()

if __name__ == "__main__":
    main()
