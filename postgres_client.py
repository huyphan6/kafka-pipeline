import matplotlib.pyplot as plt
import pandas as pd
import psycopg2
import os
from dotenv import load_dotenv

# Database Access Class
# Instantiates one connection to execute multiple queries
class PostgresClient:
    def __init__(self):
        load_dotenv()
        
        # Creates a connection to the PSQL database
        # The connector is an object that represents an active connection to the DB
        # It manages network connections, auth, and state session
        self.connector = psycopg2.connect(
                                    database=os.getenv("DB_NAME"), 
                                    user=os.getenv("POSTGRES_USER"), 
                                    password=os.getenv("POSTGRES_PASSWORD"),
                                    port=os.getenv("DB_PORT"),
                                    host=os.getenv("DB_HOST")
                                    )
        
        # The cursor is an object that executes SQL queries
        # It is an interface used to interact with the DB
        self.cursor = self.connector.cursor()
    
    def close(self):
        self.connector.close()
        
    def execute_query(self, query: str) -> list:
        try:
            self.cursor.execute(query)
            result = self.cursor.fetchall()
        finally:
            self.close()
        return result
    
    def query_to_dataframe(self, query: str, params=None):
        return pd.read_sql_query(query, self.connector, params=params)