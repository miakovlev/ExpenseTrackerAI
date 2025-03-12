import base64
import io
import logging

import matplotlib.pyplot as plt
from telegram import ReplyKeyboardMarkup, Update
from telegram.ext import Application, CallbackContext, CommandHandler, MessageHandler, filters

from config.config import TELEGRAM_TOKEN
from database.db import PostgresConnector
from database.queries import store_receipt_in_db
from openai_integration.openai_client import process_expense

logging.basicConfig(level=logging.INFO)

EXPENSE_BUTTON = [["Add Expense"], ["View Spending Chart"]]


async def start(update: Update, context: CallbackContext) -> None:
    """
    Handles the /start command, sending a welcome message with buttons.
    """
    reply_markup = ReplyKeyboardMarkup(EXPENSE_BUTTON, resize_keyboard=True, one_time_keyboard=False)
    await update.message.reply_text(
        "Welcome! This bot helps you track your expenses. Press 'Add Expense' and then send a receipt photo or text.",
        reply_markup=reply_markup,
    )


async def handle_expense(update: Update, context: CallbackContext) -> None:
    """
    Processes messages containing expense data.
    If the user sends a photo or text (excluding "View Spending Chart" and "Add Expense"),
    it attempts to analyze the receipt. If the receipt is invalid, an error message is returned.
    """
    if update.edited_message:
        return

    text_input = None
    image_bytes = None
    message_prefix = None

    if update.message.photo:
        photo_file = await update.message.photo[-1].get_file()
        image_bytes = await photo_file.download_as_bytearray()

        # Use the photo caption as text input if provided; otherwise, use a default message
        text_input = update.message.caption if update.message.caption else "Extract and analyze this receipt."
        message_prefix = "Receipt processed"

    elif update.message.text and update.message.text not in ["Add Expense", "View Spending Chart"]:
        text_input = update.message.text
        message_prefix = "Expense recorded"

    else:
        # If the message does not match the expected input, ignore it
        return

    receipt_data = process_expense(text=text_input, image_bytes=image_bytes)
    if receipt_data.get("error") == "Invalid receipt":
        error_message = (
            "❌ The provided image does not appear to be a valid receipt."
            if image_bytes
            else "❌ The provided text does not appear to be a valid receipt."
        )
        await update.message.reply_text(error_message)
        return

    # Append user data for database storage
    receipt_data["user_id"] = update.message.chat.id
    receipt_data["username"] = update.message.chat.username

    receipt_id = store_receipt_in_db(receipt_data)

    items_text = "\n".join(
        [
            f"- {item['name']}: {item['price']} {item['currency']} ({item['category']} → {item['subcategory']})"
            for item in receipt_data.get("items", [])
        ]
    )

    await update.message.reply_text(
        f"✅ {message_prefix} (ID: {receipt_id}).\n\n"
        f"Comment: {receipt_data.get('user_comment', 'No comment')}\n"
        "Items:\n" + items_text
    )


async def handle_spending_chart(update: Update, context: CallbackContext) -> None:
    """
    Handles the request to send a spending chart for the last 2 weeks, 1 month, or 3 months.
    """
    logging.info(f"handle_spending_chart triggered with message: '{update.message.text}'")
    # Example data retrieval logic (you'll need to implement this)
    spending_data = get_spending_data()  # Implement this function to fetch data from your database

    # Generate pie chart
    labels = list(spending_data.keys())
    sizes = list(spending_data.values())

    fig, ax = plt.subplots()
    ax.pie(sizes, labels=labels, autopct="%1.1f%%", startangle=90)
    ax.axis("equal")  # Equal aspect ratio ensures that pie is drawn as a circle.

    # Save the pie chart to a BytesIO object
    buf = io.BytesIO()
    plt.savefig(buf, format="png")
    buf.seek(0)
    buf.name = "chart.png"  # Set a name attribute for Telegram
    plt.close(fig)

    # Send the pie chart as a photo using the BytesIO object directly
    await update.message.reply_photo(photo=buf)


def get_spending_data():
    """
    Fetches spending data from the database and returns it as a dictionary.
    This function queries spending per category (in EUR) for the last 30 days.

    It joins the items table with the receipts table based on the receipt_id, then sums the item_price
    for each category where the receipt's created_at is within the last 30 days and the item currency is 'EUR'.
    """
    query = """
        SELECT i.category, SUM(i.item_price) AS total_spending
        FROM expensetrackerai_items i
        JOIN expensetrackerai_receipts r ON i.receipt_id = r.id
        WHERE r.created_at >= NOW() - INTERVAL '30 days'
          AND i.item_currency = 'EUR'
        GROUP BY i.category;
    """
    with PostgresConnector() as db:
        result = db.fetch(query)

    # Convert the list of tuples to a dictionary
    spending_data = {category: float(total_spending) for category, total_spending in result}
    return spending_data


def main() -> None:
    """
    Initializes the bot and registers handlers.
    """
    application = Application.builder().token(TELEGRAM_TOKEN).build()
    application.add_handler(CommandHandler("start", start))

    # Handler for the /view_spending_chart command
    application.add_handler(CommandHandler("view_spending_chart", handle_spending_chart))

    # Handler for the "View Spending Chart" text message
    application.add_handler(
        MessageHandler(filters.TEXT & filters.Regex("(?i)^View Spending Chart$"), handle_spending_chart)
    )

    # Handler for all other messages (text and photos), excluding the spending chart request
    application.add_handler(
        MessageHandler((filters.TEXT | filters.PHOTO) & ~filters.Regex("(?i)^View Spending Chart$"), handle_expense)
    )

    application.run_polling()


if __name__ == "__main__":
    main()
