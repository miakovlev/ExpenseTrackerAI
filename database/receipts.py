from datetime import datetime
import pytz
from database.db import PostgresConnector

def store_receipt(json_response: dict) -> int:
    """Store receipt data in the database and return the generated ID."""
    cyprus_tz = pytz.timezone("Asia/Nicosia")
    current_time = datetime.now(cyprus_tz).strftime("%Y-%m-%d %H:%M:%S")

    total_price = float(json_response.get("total_price", 0))
    currency = json_response.get("currency", "EUR")
    total_price_euro = float(json_response.get("total_price_euro", 0))
    user_comment = json_response.get("user_comment", "")
    user_id = json_response.get("user_id")
    username = json_response.get("username")

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
        db.conn.commit()
        return receipt_id

def get_receipt(receipt_id: int):
    """Retrieve receipt data by ID."""
    # Implementation here
    pass 