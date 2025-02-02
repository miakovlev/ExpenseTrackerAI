import os

import psycopg2

from bot.config import DB_HOST, DB_NAME, DB_PASSWORD, DB_PORT, DB_USER


def get_connection():
    """
    Creates a new psycopg2 connection using environment variables.

    Returns:
        psycopg2.extensions.connection: A new connection to PostgreSQL.
    """
    return psycopg2.connect(dbname=DB_NAME, user=DB_USER, password=DB_PASSWORD, host=DB_HOST, port=DB_PORT)
