from datetime import datetime, timezone

import pytz

from database.db import get_connection


def create_tables():
    """
    Creates the necessary database tables for the ExpenseTrackerAI project if they do not exist.
    """
    create_receipts_table = """
    CREATE TABLE IF NOT EXISTS expensetrackerai_receipts (
        id SERIAL PRIMARY KEY,
        created_at TIMESTAMP NOT NULL,
        total_price DOUBLE PRECISION,
        currency VARCHAR(10),
        total_price_euro DOUBLE PRECISION,
        user_comment TEXT
    );
    """
    create_items_table = """
    CREATE TABLE IF NOT EXISTS expensetrackerai_items (
        id SERIAL PRIMARY KEY,
        receipt_id INTEGER NOT NULL,
        item_name TEXT,
        item_price DOUBLE PRECISION,
        item_currency VARCHAR(10),
        category VARCHAR(100),
        subcategory VARCHAR(100),
        FOREIGN KEY (receipt_id) REFERENCES expensetrackerai_receipts (id) ON DELETE CASCADE
    );
    """
    conn = get_connection()
    try:
        with conn:
            with conn.cursor() as cur:
                cur.execute(create_receipts_table)
                cur.execute(create_items_table)
    finally:
        conn.close()


def store_receipt_in_db(json_response: dict) -> int:
    """
    Stores receipt data (parsed JSON) into the PostgreSQL database for the ExpenseTrackerAI project.

    Args:
        json_response (dict): The JSON with keys such as:
        {
        "total_price": "1.7",
        "currency": "EUR",
        "total_price_euro": "1.70",
        "user_comment": "Purchase at supermarket",
        "items": [
            {"name": "Milk", "price": "1", "currency": "EUR", "category": "Groceries", "subcategory": "Dairy"},
            {"name": "Bread", "price": "0.7", "currency": "EUR", "category": "Groceries", "subcategory": "Bakery"}
        ]
        }

    Returns:
        int: The generated ID for this receipt.
    """
    cyprus_tz = pytz.timezone("Asia/Nicosia")
    current_time = datetime.now(cyprus_tz).strftime("%Y-%m-%d %H:%M:%S")

    total_price = float(json_response.get("total_price", 0))
    currency = json_response.get("currency", "EUR")
    total_price_euro = float(json_response.get("total_price_euro", 0))
    user_comment = json_response.get("user_comment", "")

    conn = get_connection()
    receipt_id = None
    try:
        with conn:
            with conn.cursor() as cur:
                insert_receipt_query = """
                    INSERT INTO expensetrackerai_receipts (
                        created_at, total_price, currency, total_price_euro, user_comment
                    ) VALUES (%s, %s, %s, %s, %s)
                    RETURNING id;
                """
                cur.execute(insert_receipt_query, (current_time, total_price, currency, total_price_euro, user_comment))
                receipt_id = cur.fetchone()[0]

                for item_data in json_response.get("items", []):
                    item_name = item_data.get("name", "Unknown item")
                    item_price = float(item_data.get("price", 0))
                    item_currency = item_data.get("currency", "EUR")
                    category = item_data.get("category", "Other")
                    subcategory = item_data.get("subcategory", "Other")

                    insert_item_query = """
                        INSERT INTO expensetrackerai_items (
                            receipt_id, item_name, item_price, item_currency, category, subcategory
                        ) VALUES (%s, %s, %s, %s, %s, %s)
                    """
                    cur.execute(
                        insert_item_query, (receipt_id, item_name, item_price, item_currency, category, subcategory)
                    )
    finally:
        conn.close()

    return receipt_id


if __name__ == "__main__":
    sample_response = {
        "total_price": "1.7",
        "currency": "EUR",
        "total_price_euro": "1.70",
        "user_comment": "Purchase at supermarket",
        "items": [
            {"name": "Milk", "price": "1", "currency": "EUR", "category": "Groceries", "subcategory": "Dairy"},
            {"name": "Bread", "price": "0.7", "currency": "EUR", "category": "Groceries", "subcategory": "Bakery"},
        ],
    }

    create_tables()
    generated_id = store_receipt_in_db(sample_response)
    print(f"Receipt saved with ID: {generated_id}")
