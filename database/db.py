import psycopg2

from config.config import POSTGRES_DB, POSTGRES_USER, POSTGRES_PASSWORD, POSTGRES_HOST, POSTGRES_PORT


def get_connection():
    """
    Creates a new psycopg2 connection using environment variables.

    Returns:
        psycopg2.extensions.connection: A new connection to PostgreSQL.
    """
    return psycopg2.connect(dbname=POSTGRES_DB, user=POSTGRES_USER, password=POSTGRES_PASSWORD, host=POSTGRES_HOST, port=POSTGRES_PORT)
