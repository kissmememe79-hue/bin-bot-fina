import os
import httpx
import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

# 获取环境变量 TOKEN
TOKEN = os.getenv("TOKEN")
if not TOKEN:
    raise RuntimeError("TOKEN 未设置")
else:
    print("TOKEN 已成功获取")

BIN_API = "https://lookup.binlist.net/{}"

# BIN卡组织的中文映射
card_name_map = {
    "VISA": "维萨卡",
    "MASTERCARD": "万事达卡",
    "AMERICAN EXPRESS": "美国运通",
    "JCB": "日本国际卡",
    "DISCOVER": "发现卡",
    "MAESTRO": "梅斯特罗卡",
    "INTERAC": "国际卡",
    "ELO": "ELO 卡",
    "CHINA UNIONPAY": "中国银联",
    "UPI": "UPI卡",
}

# 欢迎页面
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[InlineKeyboardButton("🔍 查询 BIN", callback_data="bin")]]
    await update.message.reply_text(
        "欢迎使用 BIN 查询机器人 🤖\n\n直接发送 **前6位 BIN** 即可查询\n可一次发送多个（空格分隔）",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="Markdown"
    )

# 处理用户查询 BIN
async def query_bin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    bins = update.message.text.strip().split()
    results = []

    async with httpx.AsyncClient() as client:
        for b in bins:
            if not b.isdigit() or len(b) < 6:
                continue
            try:
                r = await client.get(BIN_API.format(b))
                if r.status_code != 200:
                    continue
                d = r.json()

                # 获取卡组织的中文名称
                translated_brand = card_name_map.get(d.get('scheme', '').upper(), d.get('scheme', '未知'))

                results.append(
                    f"〔🌱〕 BIN ➤ {b}\n"
                    f"〔💳〕 卡组织 ➤ {translated_brand}（{d.get('scheme', '未知').upper()}）\n"
                    f"〔💰〕 卡类型 ➤ {d.get('type', '未知')}（类型）\n"
                    f"〔🏆〕 卡等级 ➤ {d.get('brand', '未知')}（等级）\n"
                    f"〔🏦〕 发行银行 ➤ {d.get('bank', {}).get('name', '未知')}（银行）\n"
                    f"〔🌍〕 国家 ➤ {d.get('country', {}).get('name', '未知')}（国家）\n"
                )
            except Exception as e:
                print(f"查询BIN {b} 时发生错误: {e}") # 打印错误信息

    # 返回查询结果
    if results:
        await update.message.reply_text("\n\n".join(results))
    else:
        await update.message.reply_text("未查询到有效 BIN")

# 启动机器人
async def run_bot():
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, query_bin))
    await app.run_polling(drop_pending_updates=True)
# 运行
if __name__ == "__main__":
    asyncio.run(run_bot()) # 直接使用 asyncio.run() 来启动机器人
