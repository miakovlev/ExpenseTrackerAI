# database/postgres_connector.py
import pandas as pd
import psycopg2

from config.config import POSTGRES_DB, POSTGRES_HOST, POSTGRES_PASSWORD, POSTGRES_PORT, POSTGRES_USER


class PostgresConnector:
    """
    A class to handle PostgreSQL connections and queries.
    Supports fetching query results and returning a pandas DataFrame.
    Implements context management to ensure connections are properly closed.
    """

    def __enter__(self):
        self.conn = psycopg2.connect(
            dbname=POSTGRES_DB, user=POSTGRES_USER, password=POSTGRES_PASSWORD, host=POSTGRES_HOST, port=POSTGRES_PORT
        )
        self.cursor = self.conn.cursor()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.close()

    def close(self):
        """Close the database cursor and connection."""
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()

    def fetch(self, query, params=None):
        """
        Execute a SQL query and return all fetched rows.

        :param query: SQL query string.
        :param params: Optional query parameters.
        :return: List of tuples containing query results.
        """
        self.cursor.execute(query, params)
        return self.cursor.fetchall()

    def get_dataframe(self, query, params=None):
        """
        Execute a SQL query and return the results as a pandas DataFrame.

        :param query: SQL query string.
        :param params: Optional query parameters.
        :return: pandas DataFrame with query results.
        """
        df = pd.read_sql_query(query, self.conn, params=params)
        return df


if __name__ == "__main__":
    # Sample usage of the connector
    sample_query = "SELECT * FROM expensetrackerai_receipts LIMIT 10;"
    with PostgresConnector() as db:
        # Retrieve data as list of tuples
        data = db.fetch(sample_query)
        print("Result from fetch():", data)

        # Retrieve data as a pandas DataFrame
        df = db.get_dataframe(sample_query)
        print("Result as DataFrame:")
        print(df)
