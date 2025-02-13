import logging

from telegram import ReplyKeyboardMarkup, Update
from telegram.ext import Application, CallbackContext, CommandHandler, MessageHandler, filters

from config.config import TELEGRAM_TOKEN
from database.queries import store_receipt_in_db
from openai_integration.openai_client import process_expense

logging.basicConfig(level=logging.INFO)

EXPENSE_BUTTON = [["Add Expense"]]


async def start(update: Update, context: CallbackContext) -> None:
    """
    Handles the /start command, sending a welcome message with the "Add Expense" button.
    """
    reply_markup = ReplyKeyboardMarkup(EXPENSE_BUTTON, resize_keyboard=True, one_time_keyboard=False)
    await update.message.reply_text(
        "Welcome! This bot helps you track your expenses. Press 'Add Expense' and then send a receipt photo or text.",
        reply_markup=reply_markup,
    )


async def handle_expense(update: Update, context: CallbackContext) -> None:
    """
    Processes user input after pressing 'Add Expense'. It handles both text and photo messages.
    For photo messages, if a caption is provided, it uses that as the text input;
    otherwise, it uses a default instruction.
    If the returned response contains an error, it does not save data to the database.
    """
    if update.edited_message:
        return

    text_input = None
    image_bytes = None
    message_prefix = None

    if update.message.photo:
        photo_file = await update.message.photo[-1].get_file()
        image_bytes = await photo_file.download_as_bytearray()

        # Use the photo caption as text input if provided
        text_input = update.message.caption if update.message.caption else "Extract and analyze this receipt."
        message_prefix = "Receipt processed"

    elif update.message.text and update.message.text != "Add Expense":
        text_input = update.message.text
        message_prefix = "Expense recorded"

    else:
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

    # Append additional user info to receipt_data for database storage
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


def main() -> None:
    """
    Initializes the bot and starts polling for updates.
    """
    application = Application.builder().token(TELEGRAM_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT | filters.PHOTO, handle_expense))
    application.run_polling()


if __name__ == "__main__":
    main()
