#!/usr/bin/env python
"""
Database initialization script for ExpenseTrackerAI.
Run this script to create all necessary database tables if they don't exist.
"""
import logging
from database.queries import create_tables
from database.db import PostgresConnector

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def initialize_database():
    """Initialize the database by creating necessary tables if they don't exist."""
    logger.info("Initializing database - checking for required tables...")
    
    try:
        create_tables()
        logger.info("Database tables successfully created or already exist.")
        
        # Verify tables exist by checking their structure
        with PostgresConnector() as db:
            db.cursor.execute(
                "SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'expensetrackerai_receipts')"
            )
            receipts_exists = db.cursor.fetchone()[0]
            
            db.cursor.execute(
                "SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'expensetrackerai_items')"
            )
            items_exists = db.cursor.fetchone()[0]
            
            if receipts_exists and items_exists:
                logger.info("Verification successful: All required tables exist")
            else:
                logger.warning("Verification failed: Some tables are missing")
    
    except Exception as e:
        logger.error(f"Error initializing database: {e}")
        raise

if __name__ == "__main__":
    initialize_database() 