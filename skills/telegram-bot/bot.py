"""
agents/telegram_bot.py
Block 1 & 2 — Part 2: TG Bot + Mini App Webhook
Commands: /start, /balance, /quote, /status, /dudcheck, /cow, /revenue, /budget, /manual
"""
import logging, os, json, hmac, hashlib
from telegram import Update, InlineQueryResultArticle, InputTextMessageContent, InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, InlineQueryHandler, MessageHandler, filters

log = logging.getLogger("telegram_bot")

# Config from environment (Doppler)
TOKEN = os.getenv("TG_BOT_TOKEN", "7364528190:AAH-test-token")
WEBAPP_URL = os.getenv("TG_WEBAPP_URL", "http://15.223.49.28:8000/tg")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("Open Miner", web_app=WebAppInfo(url=WEBAPP_URL))],
        [InlineKeyboardButton("Dashboard", web_app=WebAppInfo(url=f"{WEBAPP_URL}/dashboard"))],
        [InlineKeyboardButton("Manual", web_app=WebAppInfo(url=f"{WEBAPP_URL}/manual"))]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "Welcome to SuperAgentOS\nFlash Loan Solver · Base\n\nUse buttons below or /help for commands.",
        reply_markup=reply_markup
    )

async def balance(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Mock data or read from /tmp/budget_state.json
    await update.message.reply_text("Balance: $0.50 remaining\nGas Spent: $0.00\nProfit: $0.00")

async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Status: Working\nVerdict: Pending $0.50 test")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = (
        "/start - Welcome & Menu\n"
        "/balance - Current test budget\n"
        "/status - Working/Effective/Dud\n"
        "/quote - Get current solver price\n"
        "/dudcheck - Check test results\n"
        "/cow - Onboarding status\n"
        "/revenue - Today's earnings\n"
        "/budget - Resource caps\n"
        "/manual - Link to guide"
    )
    await update.message.reply_text(help_text)

async def inline_query(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.inline_query.query
    results = [
        InlineQueryResultArticle(
            id="1",
            title="Solver Status",
            input_message_content=InputTextMessageContent("SuperAgentOS: Working | Balance $0.50")
        ),
        InlineQueryResultArticle(
            id="2",
            title="Get Quote",
            input_message_content=InputTextMessageContent("Current Quote: $1.99 (Test Mode)")
        )
    ]
    await update.inline_query.answer(results, cache_time=90)

def run_bot():
    app = ApplicationBuilder().token(TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("balance", balance))
    app.add_handler(CommandHandler("status", status))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(InlineQueryHandler(inline_query))
    
    log.info("Telegram Bot starting...")
    app.run_polling()

if __name__ == "__main__":
    run_bot()
