import base64
import json

import openai

from bot.constants import CATEGORIES
from config.config import OPENAI_API_KEY

openai.api_key = OPENAI_API_KEY
client_openai = openai.OpenAI(api_key=OPENAI_API_KEY)


def generate_chat_completion(client: openai.OpenAI, message: dict, model: str = "gpt-4o-mini") -> dict:
    """
    Sends a chat completion request to OpenAI API and returns the response.

    Args:
        client (openai.OpenAI): The OpenAI API client.
        message (dict[str, Any]): The message payload for the API request.
        model (str, optional): The model to use. Defaults to "gpt-4o-mini".

    Returns:
        dict[str, Any]: The API response parsed as a JSON object.
    """
    response = client.chat.completions.create(model=model, messages=[message], response_format={"type": "json_object"})
    return json.loads(response.choices[0].message.content)


def process_expense(text: str, image_bytes: bytes | None = None) -> dict:
    """
    Processes expense information from text (and optionally an image) and returns structured expense data.

    Args:
        text (str): The expense information in natural language.
        image_bytes (bytes, optional): The image file as a byte stream. Defaults to None.

    Returns:
        dict: A JSON object with keys: 'total_price', 'currency', 'total_price_euro', 'items', 'user_comment'.
              Each item in 'items' includes 'name', 'price', 'currency', 'category', and 'subcategory'.
              If the image does not appear to be a valid receipt, returns an object with an 'error' key.
    """
    example_input = "Starbucks Croissant 1.20 euro and Latte 3.50 euro"
    example_output = {
        "total_price": "4.70",
        "currency": "EUR",
        "total_price_euro": "4.70",
        "items": [
            {
                "name": "Croissant",
                "price": "1.20",
                "currency": "EUR",
                "category": "Food & Drinks",
                "subcategory": "Groceries & Delivery",
            },
            {"name": "Latte", "price": "3.50", "currency": "EUR", "category": "Food & Drinks", "subcategory": "Coffee"},
        ],
        "user_comment": "Starbucks purchase",
    }
    # Add instruction for invalid receipt detection.
    extra_instruction = (
        "If the provided image does not contain receipt-related text, or if the provided text does not appear to be a valid receipt, "
        "return a JSON object with the key 'error' and the value 'Invalid receipt'.\n"
        "If the currency cannot be determined, default to EUR.\n"
        "Ensure that the entire response is strictly in English."
    )
    prompt = (
        f"Analyze the following expense information: {text}\n\n"
        "Available categories and subcategories:\n"
        f"{json.dumps(CATEGORIES, ensure_ascii=False, indent=2)}\n\n"
        "Return a JSON object with the following keys: 'total_price', 'currency', 'total_price_euro', 'items', 'user_comment'.\n"
        "Each item in 'items' should include 'name', 'price', 'currency', 'category', and 'subcategory'.\n"
        "Ensure that 'category' and 'subcategory' are chosen only from the provided list.\n\n"
        f"{extra_instruction}\n\n"
        f"Example input:\n{example_input}\n\n"
        "Example output:\n"
        f"{json.dumps(example_output, ensure_ascii=False, indent=2)}"
    )

    if image_bytes:
        base64_image = base64.b64encode(image_bytes).decode("utf-8")
        message_content = [
            {
                "type": "text",
                "text": prompt,
            },
            {
                "type": "image_url",
                "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"},
            },
        ]
        message = {"role": "user", "content": message_content}
    else:
        message = {"role": "user", "content": prompt}

    result = generate_chat_completion(client=client_openai, message=message)
    return result
