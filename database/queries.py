import uuid
from datetime import datetime

from database.db import get_connection


def create_tables():
    """
    Creates the necessary database tables if they do not exist.
    """
    create_receipts_table = """
    CREATE TABLE IF NOT EXISTS receipts (
        id SERIAL PRIMARY KEY,
        check_id UUID NOT NULL UNIQUE,
        created_at TIMESTAMP NOT NULL,
        total_price DOUBLE PRECISION,
        currency VARCHAR(10),
        total_price_euro DOUBLE PRECISION,
        user_comment TEXT
    );
    """
    create_items_table = """
    CREATE TABLE IF NOT EXISTS items (
        id SERIAL PRIMARY KEY,
        receipt_id UUID NOT NULL,
        item_name TEXT,
        item_price DOUBLE PRECISION,
        item_currency VARCHAR(10),
        category VARCHAR(100),
        subcategory VARCHAR(100),
        FOREIGN KEY (receipt_id) REFERENCES receipts (check_id) ON DELETE CASCADE
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


def store_receipt_in_db(json_response: dict) -> str:
    """
    Stores receipt data (parsed JSON) into the PostgreSQL database.

    Args:
        json_response (dict): The JSON with keys like:
          {
            "total_price": "4.70",
            "currency": "EUR",
            "total_price_euro": "4.70",
            "items": [...],
            "user_comment": "...",
          }

    Returns:
        str: The generated UUID (check_id) for this receipt.
    """
    check_id = uuid.uuid4()
    current_time = datetime.now()

    total_price = float(json_response.get("total_price", 0))
    currency = json_response.get("currency", "EUR")
    total_price_euro = float(json_response.get("total_price_euro", 0))
    user_comment = json_response.get("user_comment", "")

    conn = get_connection()
    try:
        with conn:
            with conn.cursor() as cur:
                insert_receipt_query = """
                    INSERT INTO receipts (
                        check_id, created_at, total_price, currency, total_price_euro, user_comment
                    ) VALUES (%s, %s, %s, %s, %s, %s)
                """
                cur.execute(
                    insert_receipt_query,
                    (check_id, current_time, total_price, currency, total_price_euro, user_comment),
                )

                for item_data in json_response.get("items", []):
                    item_name = item_data.get("name", "Unknown item")
                    item_price = float(item_data.get("price", 0))
                    item_currency = item_data.get("currency", "EUR")
                    category = item_data.get("category", "Other")
                    subcategory = item_data.get("subcategory", "Other")

                    insert_item_query = """
                        INSERT INTO items (
                            receipt_id, item_name, item_price, item_currency, category, subcategory
                        ) VALUES (%s, %s, %s, %s, %s, %s)
                    """
                    cur.execute(
                        insert_item_query, (check_id, item_name, item_price, item_currency, category, subcategory)
                    )
    finally:
        conn.close()

    return str(check_id)
