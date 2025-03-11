# queries.py
from datetime import datetime
import pytz
from database.db import PostgresConnector

def create_tables():
    """
    Create the necessary database tables for the ExpenseTrackerAI project if they do not exist.
    """
    create_receipts_table = """
    CREATE TABLE IF NOT EXISTS expensetrackerai_receipts (
        id SERIAL PRIMARY KEY,
        created_at TIMESTAMP NOT NULL,
        user_id BIGINT,
        username VARCHAR(255),
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
    with PostgresConnector() as db:
        db.cursor.execute(create_receipts_table)
        db.cursor.execute(create_items_table)
        db.conn.commit()

def store_receipt_in_db(json_response: dict) -> int:
    """
    Store receipt data (parsed JSON) into the PostgreSQL database for the ExpenseTrackerAI project.

    :param json_response: The JSON with keys such as:
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
    :return: The generated ID for this receipt.
    """
    cyprus_tz = pytz.timezone("Asia/Nicosia")
    current_time = datetime.now(cyprus_tz).strftime("%Y-%m-%d %H:%M:%S")

    total_price = float(json_response.get("total_price", 0))
    currency = json_response.get("currency", "EUR")
    total_price_euro = float(json_response.get("total_price_euro", 0))
    user_comment = json_response.get("user_comment", "")
    user_id = json_response.get("user_id")
    username = json_response.get("username")

    receipt_id = None
    with PostgresConnector() as db:
        insert_receipt_query = """
            INSERT INTO expensetrackerai_receipts (
                created_at, user_id, username, total_price, currency, total_price_euro, user_comment
            ) VALUES (%s, %s, %s, %s, %s, %s, %s)
            RETURNING id;
        """
        db.cursor.execute(
            insert_receipt_query,
            (current_time, user_id, username, total_price, currency, total_price_euro, user_comment),
        )
        receipt_id = db.cursor.fetchone()[0]

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
            db.cursor.execute(
                insert_item_query, (receipt_id, item_name, item_price, item_currency, category, subcategory)
            )
        db.conn.commit()
    return receipt_id

if __name__ == "__main__":
    # Create tables if they do not exist
    create_tables()

    sample_response = {
        "total_price": "1.7",
        "currency": "EUR",
        "total_price_euro": "1.70",
        "user_comment": "Purchase at supermarket",
        "items": [
            {"name": "Milk", "price": "1", "currency": "EUR", "category": "Groceries", "subcategory": "Dairy"},
            {"name": "Bread", "price": "0.7", "currency": "EUR", "category": "Groceries", "subcategory": "Bakery"}
        ],
    }

    generated_id = store_receipt_in_db(sample_response)
    print(f"Receipt saved with ID: {generated_id}")
