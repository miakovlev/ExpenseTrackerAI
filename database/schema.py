from database.db import PostgresConnector

def create_tables():
    """Create the necessary database tables if they don't exist."""
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