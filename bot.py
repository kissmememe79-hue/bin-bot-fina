import os
import httpx
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
import asyncio

# 获取环境变量 TOKEN
TOKEN = os.getenv("TOKEN")
if not TOKEN:
    raise RuntimeError("TOKEN 未设置")

BIN_API = "https://lookup.binlist.net/{}"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[InlineKeyboardButton("🔍 查询 BIN", callback_data="bin")]]
    await update.message.reply_text(
        "欢迎使用 BIN 查询机器人 🤖\n\n直接发送 **前6位 BIN** 即可查询\n可一次发送多个（空格分隔）",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="Markdown"
    )

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
                results.append(
                    f"〔🌱〕 BIN ➤ {b}\n"
                    f"〔💳〕 Card Brand ➤ {d.get('scheme','未知').upper()}（卡组织）\n"
                    f"〔💰〕 Card Type ➤ {d.get('type','未知')}（类型）\n"
                    f"〔🏆〕 Card Level ➤ {d.get('brand','未知')}（等级）\n"
                    f"〔🏦〕 Bank Name ➤ {d.get('bank',{}).get('name','未知')}（银行）\n"
                    f"〔🌍〕 Country ➤ {d.get('country',{}).get('name','未知')}（国家）\n"
                )
            except:
                continue

    if results:
        await update.message.reply_text("\n\n".join(results))
    else:
        await update.message.reply_text("未查询到有效 BIN")

async def run_bot():
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, query_bin))
    await app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    asyncio.run(run_bot())
