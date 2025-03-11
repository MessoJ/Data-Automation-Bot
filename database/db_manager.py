import os
import pandas as pd
import logging
from sqlalchemy import create_engine, text, MetaData, Table, inspect
from sqlalchemy.exc import SQLAlchemyError
from dotenv import load_dotenv

logger = logging.getLogger(__name__)

class DatabaseManager:
    """
    Class for managing database connections and operations.
    Provides methods for querying, inserting, and updating data.
    """
    
    def __init__(self, connection_string=None):
        """
        Initialize the DatabaseManager with a connection string.
        
        If no connection string is provided, attempts to build one from
        environment variables.
        
        Args:
            connection_string (str, optional): SQLAlchemy connection string.
        """
        load_dotenv()
        
        if connection_string:
            self.connection_string = connection_string
        else:
            # Build connection string from environment variables
            db_host = os.getenv("DB_HOST", "database-1.cxwa0k264rkw.eu-north-1.rds.amazonaws.com")
            db_port = os.getenv("DB_PORT", "5432")
            db_name = os.getenv("database-1")
            db_user = os.getenv("postgres")
            db_password = os.getenv("Minaa.2030")
            
            if not all([db_name, db_user, db_password]):
                raise ValueError("Database credentials not found in environment variables")
            
            self.connection_string = (
                f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
            )
        
        self.engine = None
        self.metadata = MetaData()
        logger.info("DatabaseManager initialized")
    
    def connect(self):
        """
        Establish a connection to the database.
        
        Returns:
            bool: True if connection successful, False otherwise.
        """
        try:
            self.engine = create_engine(self.connection_string)
            # Test connection
            with self.engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            logger.info("Successfully connected to database")
            return True
        except SQLAlchemyError as e:
            logger.error(f"Database connection error: {str(e)}")
            return False
    
    def execute_query(self, query, params=None):
        """
        Execute a SQL query and return the results as a DataFrame.
        
        Args:
            query (str): SQL query to execute.
            params (dict, optional): Parameters for the query.
        
        Returns:
            pd.DataFrame: Query results as a DataFrame.
        """
        if self.engine is None and not self.connect():
            raise ConnectionError("Database connection not established")
        
        try:
            logger.info(f"Executing query: {query}")
            if params:
                result = pd.read_sql(text(query), self.engine, params=params)
            else:
                result = pd.read_sql(text(query), self.engine)
            
            logger.info(f"Query returned {len(result)} rows")
            return result
        except SQLAlchemyError as e:
            logger.error(f"Query execution error: {str(e)}")
            raise
    
    def execute_statement(self, statement, params=None):
        """
        Execute a SQL statement (INSERT, UPDATE, DELETE).
        
        Args:
            statement (str): SQL statement to execute.
            params (dict, optional): Parameters for the statement.
        
        Returns:
            int: Number of rows affected.
        """
        if self.engine is None and not self.connect():
            raise ConnectionError("Database connection not established")
        
        try:
            with self.engine.connect() as conn:
                with conn.begin():
                    if params:
                        result = conn.execute(text(statement), params)
                    else:
                        result = conn.execute(text(statement))
                    
                    row_count = result.rowcount
                    logger.info(f"Statement affected {row_count} rows")
                    return row_count
        except SQLAlchemyError as e:
            logger.error(f"Statement execution error: {str(e)}")
            raise
    
    def get_table_schema(self, table_name):
        """
        Get the schema of a table.
        
        Args:
            table_name (str): Name of the table.
        
        Returns:
            dict: Column information for the table.
        """
        if self.engine is None and not self.connect():
            raise ConnectionError("Database connection not established")
        
        try:
            inspector = inspect(self.engine)
            columns = inspector.get_columns(table_name)
            logger.info(f"Retrieved schema for table '{table_name}'")
            return columns
        except SQLAlchemyError as e:
            logger.error(f"Error retrieving table schema: {str(e)}")
            raise
    
    def list_tables(self):
        """
        List all tables in the database.
        
        Returns:
            list: Names of all tables in the database.
        """
        if self.engine is None and not self.connect():
            raise ConnectionError("Database connection not established")
        
        try:
            inspector = inspect(self.engine)
            tables = inspector.get_table_names()
            logger.info(f"Listed {len(tables)} tables in database")
            return tables
        except SQLAlchemyError as e:
            logger.error(f"Error listing tables: {str(e)}")
