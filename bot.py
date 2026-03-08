import os
import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, CommandHandler, filters, ContextTypes

BOT_TOKEN = os.environ.get("BOT_TOKEN")
SHEET_CSV_URL = os.environ.get("SHEET_CSV_URL")

def get_products():
    response = requests.get(SHEET_CSV_URL)
    products = {}
    lines = response.text.strip().split("\n")
    for line in lines[1:]:
        parts = line.strip().split(",")
        if len(parts) >= 2:
            name = parts[0].strip().lower()
            try:
                price = float(parts[1].strip())
                products[name] = price
            except ValueError:
                pass
    return products

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Welcome to the Price Calculator Bot!\n\n"
        "Type a product and quantity like:\n"
        "`Apple 5` or `Whole Milk 3`\n\n"
        "Use /list to see all available products.",
        parse_mode="Markdown"
    )

async def list_products(update: Update, context: ContextTypes.DEFAULT_TYPE):
    products = get_products()
    if not products:
        await update.message.reply_text("No products found in the sheet.")
        return
    lines = [f"• {name.title()} — ${price:.2f}" for name, price in products.items()]
    await update.message.reply_text(
        "📦 *Available Products:*\n\n" + "\n".join(lines),
        parse_mode="Markdown"
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    parts = text.split()

    if len(parts) < 2:
        await update.message.reply_text(
            "Please type: *Product Quantity*\nExample: `Apple 5`",
            parse_mode="Markdown"
        )
        return

    try:
        quantity = float(parts[-1])
        product_name = " ".join(parts[:-1]).lower()
    except ValueError:
        await update.message.reply_text(
            "Please type: *Product Quantity*\nExample: `Apple 5`",
            parse_mode="Markdown"
        )
        return

    products = get_products()

    if product_name in products:
        price = products[product_name]
        total = price * quantity
        await update.message.reply_text(
            f"🛒 *{product_name.title()}*\n"
            f"Unit Price: ${price:.2f}\n"
            f"Quantity: {quantity:.0f}\n"
            f"💰 *Total: ${total:.2f}*",
            parse_mode="Markdown"
        )
    else:
        available = "\n".join(f"• {p.title()}" for p in products.keys())
        await update.message.reply_text(
            f"❌ *{product_name.title()}* not found.\n\n"
            f"Available products:\n{available}",
            parse_mode="Markdown"
        )

app = ApplicationBuilder().token(BOT_TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("list", list_products))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))




