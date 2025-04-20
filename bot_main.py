from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    ContextTypes,
    filters,
)
from mvrv_plot import build_mvrv_chart
from funding_data import get_funding_info
import os

BOT_TOKEN = os.getenv("BOT_TOKEN")

user_states = {}
TOP_COINS = ["BTC", "ETH", "BNB", "SOL", "XRP"]

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("📊 MVRV", callback_data="select_mvrv")],
        [InlineKeyboardButton("💰 Funding", callback_data="select_funding")]
    ]
    await update.message.reply_text("👋 Вітаю! Обери індикатор:", reply_markup=InlineKeyboardMarkup(keyboard))

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    data = query.data

    if data == "select_mvrv":
        keyboard = [[InlineKeyboardButton(coin, callback_data=f"mvrv_{coin.lower()}")] for coin in TOP_COINS]
        keyboard.append([InlineKeyboardButton("🔍 Інша монета", callback_data="mvrv_manual")])
        keyboard.append([InlineKeyboardButton("🔙 Назад", callback_data="back")])
        await query.edit_message_text("📊 Обери монету для MVRV:", reply_markup=InlineKeyboardMarkup(keyboard))
        return

    if data == "select_funding":
        keyboard = [[InlineKeyboardButton(coin, callback_data=f"funding_{coin.lower()}")] for coin in TOP_COINS]
        keyboard.append([InlineKeyboardButton("🔍 Інша монета", callback_data="funding_manual")])
        keyboard.append([InlineKeyboardButton("🔙 Назад", callback_data="back")])
        await query.edit_message_text("💰 Обери монету для Funding:", reply_markup=InlineKeyboardMarkup(keyboard))
        return

    if data == "back":
        keyboard = [
            [InlineKeyboardButton("📊 MVRV", callback_data="select_mvrv")],
            [InlineKeyboardButton("💰 Funding", callback_data="select_funding")]
        ]
        await query.edit_message_text("👋 Вітаю! Обери індикатор:", reply_markup=InlineKeyboardMarkup(keyboard))
        return

    if data.startswith("mvrv_"):
        coin = data.replace("mvrv_", "")
        if coin == "manual":
            user_states[user_id] = "waiting_for_mvrv_coin"
            await query.message.reply_text("✏️ Введи назву монети (наприклад: pepe):")
        else:
            await send_mvrv_chart(query, coin)
        return

    if data.startswith("funding_"):
        coin = data.replace("funding_", "")
        if coin == "manual":
            user_states[user_id] = "waiting_for_funding_coin"
            await query.message.reply_text("✏️ Введи назву монети (наприклад: floki):")
        else:
            await send_funding_data(query, coin)
        return

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    coin = update.message.text.strip().lower()
    if user_id not in user_states:
        await update.message.reply_text("⚠️ Обери індикатор через /start")
        return

    state = user_states.pop(user_id)
    if state == "waiting_for_mvrv_coin":
        await send_mvrv_chart(update, coin)
    elif state == "waiting_for_funding_coin":
        await send_funding_data(update, coin)

async def send_mvrv_chart(source, coin: str):
    msg = await source.message.reply_text(f"📈 Створюю графік для {coin.upper()}...")
    try:
        build_mvrv_chart(coin_id=coin)
        if os.path.exists("mvrv_chart.png"):
            with open("mvrv_chart.png", "rb") as chart:
                await source.message.reply_photo(chart)
        else:
            await source.message.reply_text("⚠️ Графік не створено.")
    except Exception as e:
        await source.message.reply_text(f"❌ Помилка: {str(e)}")
    finally:
        await msg.delete()

async def send_funding_data(source, coin: str):
    msg = await source.message.reply_text(f"📡 Завантажую Funding для {coin.upper()}...")
    try:
        funding_rate, oi = get_funding_info(coin)
        arrow = "📈" if funding_rate > 0 else "📉"
        oi_display = f"${oi:.0f}M" if oi is not None else "Невідомо"
        msg_text = (
            f"{arrow} *Funding Rate (24h):* `{funding_rate:.3f}%`\\n"
            f"📊 *Open Interest:* `{oi_display}`\\n"
            f"💎 *Монета:* `{coin.upper()}`"
        )
        await source.message.reply_markdown(msg_text)
    except Exception as e:
        await source.message.reply_text(f"❌ Помилка: {str(e)}")
    finally:
        await msg.delete()

if __name__ == "__main__":
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    print("✅ Бот з меню запущено. Готовий до роботи!")
    app.run_polling()
