# queries.py
from datetime import datetime

import pytz

from database.db import PostgresConnector
from database.schema import create_tables
from database.receipts import store_receipt
from database.items import store_items


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
    
    This is a backward-compatibility wrapper for the new store_receipt and store_items functions.
    
    :param json_response: The JSON with receipt and item data
    :return: The generated ID for this receipt.
    """
    # Store receipt and get receipt_id
    receipt_id = store_receipt(json_response)
    
    # Store associated items
    items = json_response.get("items", [])
    store_items(receipt_id, items)
    
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
            {"name": "Bread", "price": "0.7", "currency": "EUR", "category": "Groceries", "subcategory": "Bakery"},
        ],
    }

    generated_id = store_receipt_in_db(sample_response)
    print(f"Receipt saved with ID: {generated_id}")
