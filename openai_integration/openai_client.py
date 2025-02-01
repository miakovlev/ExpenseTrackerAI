import base64
import json

import openai

from bot.config import OPENAI_API_KEY
from bot.constants import CATEGORIES

openai.api_key = OPENAI_API_KEY
client = openai.OpenAI(api_key=OPENAI_API_KEY)


def process_expense(text: str, image_bytes: bytes = None) -> dict:
    """
    Processes expense information from text (and optionally an image) and returns structured expense data.

    Args:
        text (str): The expense information in natural language.
        image_bytes (bytes, optional): The image file as a byte stream. Defaults to None.

    Returns:
        dict: A JSON object with keys: 'items', 'comment'.
              Each item in 'items' includes 'name', 'price', 'currency', 'category', and 'subcategory'.
    """
    example_input = "Starbucks Croissant 1.20 euro and Latte 3.50 euro"
    example_output = {
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
        "comment": "Starbucks purchase",
    }
    prompt = (
        f"Analyze the following expense information: {text}\n\n"
        "Available categories and subcategories:\n"
        f"{json.dumps(CATEGORIES, ensure_ascii=False, indent=2)}\n\n"
        "Return a JSON object with the following keys: "
        "'items', 'comment'.\n"
        "Each item in 'items' should include 'name', 'price', 'currency', 'category', and 'subcategory'.\n"
        "Ensure that 'category' and 'subcategory' are chosen only from the provided list.\n\n"
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

    response = client.chat.completions.create(
        model="gpt-4o-mini", messages=[message], response_format={"type": "json_object"}
    )
    res = json.loads(response.choices[0].message.content)
    return res
