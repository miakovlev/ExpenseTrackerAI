from database.db import PostgresConnector

def store_items(receipt_id: int, items: list) -> None:
    """Store item data for a given receipt."""
    with PostgresConnector() as db:
        for item_data in items:
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