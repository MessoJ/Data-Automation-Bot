"""
Tests for the database module.
"""
import unittest
import os
import sqlite3
from unittest.mock import patch, MagicMock
import pandas as pd
from data_automation_bot.database.db_manager import DatabaseManager

class TestDatabaseManager(unittest.TestCase):
    """Test cases for the DatabaseManager class."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Use in-memory SQLite database for testing
        self.db_config = {
            'database': {
                'type': 'sqlite',
                'connection_string': ':memory:',
                'pool_size': 1
            }
        }
        
        with patch('data_automation_bot.config.Config.get_config', return_value=self.db_config):
            self.db_manager = DatabaseManager()
        
        # Create a test table
        self.db_manager.execute('''
            CREATE TABLE test_table (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                value REAL
            )
        ''')
    
    def test_execute(self):
        """Test the execute method for inserting data."""
        # Insert test data
        self.db_manager.execute(
            "INSERT INTO test_table (name, value) VALUES (?, ?)",
            params=("Test Item", 42.5)
        )
        
        # Verify data was inserted
        result = self.db_manager.execute("SELECT * FROM test_table")
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]['name'], "Test Item")
        self.assertEqual(result[0]['value'], 42.5)
    
    def test_execute_many(self):
        """Test the execute_many method for bulk inserting data."""
        # Prepare test data
        test_data = [
            ("Item 1", 10.5),
            ("Item 2", 20.75),
            ("Item 3", 30.25)
        ]
        
        # Insert test data
        self.db_manager.execute_many(
            "INSERT INTO test_table (name, value) VALUES (?, ?)",
            params=test_data
        )
        
        # Verify data was inserted
        result = self.db_manager.execute("SELECT * FROM test_table ORDER BY id")
        self.assertEqual(len(result), 3)
        self.assertEqual(result[0]['name'], "Item 1")
        self.assertEqual(result[1]['name'], "Item 2")
        self.assertEqual(result[2]['name'], "Item 3")
    
    def test_execute_script(self):
        """Test the execute_script method for running SQL scripts."""
        # Create a script with multiple statements
        script = """
        INSERT INTO test_table (name, value) VALUES ('Script Item 1', 11.1);
        INSERT INTO test_table (name, value) VALUES ('Script Item 2', 22.2);
        UPDATE test_table SET value = 33.3 WHERE name = 'Script Item 1';
        """
        
        # Execute the script
        self.db_manager.execute_script(script)
        
        # Verify results
        result = self.db_manager.execute("SELECT * FROM test_table ORDER BY id")
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]['name'], "Script Item 1")
        self.assertEqual(result[0]['value'], 33.3)
        self.assertEqual(result[1]['name'], "Script Item 2")
        self.assertEqual(result[1]['value'], 22.2)
    
    def test_dataframe_to_sql(self):
        """Test saving a DataFrame to the database."""
        # Create test DataFrame
        df = pd.DataFrame({
            'name': ['DataFrame Item 1', 'DataFrame Item 2'],
            'value': [55.5, 66.6]
        })
        
        # Save DataFrame to database
        self.db_manager.dataframe_to_sql(df, 'test_table', if_exists='append')
        
        # Verify results
        result = self.db_manager.execute("SELECT * FROM test_table ORDER BY id")
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]['name'], "DataFrame Item 1")
        self.assertEqual(result[1]['name'], "DataFrame Item 2")
    
    def test_query_to_dataframe(self):
        """Test retrieving query results as DataFrame."""
        # Insert test data
        test_data = [
            ("DF Query 1", 10.1),
            ("DF Query 2", 20.2),
            ("DF Query 3", 30.3)
        ]
        
        self.db_manager.execute_many(
            "INSERT INTO test_table (name, value) VALUES (?, ?)",
            params=test_data
        )
        
        # Retrieve as DataFrame
        df = self.db_manager.query_to_dataframe("SELECT * FROM test_table ORDER BY value")
        
        # Verify DataFrame
        self.assertEqual(len(df), 3)
        self.assertEqual(df['name'].iloc[0], "DF Query 1")
        self.assertEqual(df['name'].iloc[1], "DF Query 2")
        self.assertEqual(df['name'].iloc[2], "DF Query 3")
        self.assertEqual(df['value'].iloc[0], 10.1)
    
    def test_transaction(self):
        """Test transaction handling."""
        # Start a transaction
        self.db_manager.begin_transaction()
        
        try:
            # Execute statements in transaction
            self.db_manager.execute(
                "INSERT INTO test_table (name, value) VALUES (?, ?)",
                params=("Transaction Item 1", 77.7)
            )
            self.db_manager.execute(
                "INSERT INTO test_table (name, value) VALUES (?, ?)",
                params=("Transaction Item 2", 88.8)
            )
            
            # Commit the transaction
            self.db_manager.commit()
        except Exception:
            # Rollback on error
            self.db_manager.rollback()
            raise
        
        # Verify results after commit
        result = self.db_manager.execute("SELECT * FROM test_table ORDER BY id")
        self.assertEqual(len(result), 2)
    
    def test_transaction_rollback(self):
        """Test transaction rollback."""
        # Insert initial data
        self.db_manager.execute(
            "INSERT INTO test_table (name, value) VALUES (?, ?)",
            params=("Before Rollback", 99.9)
        )
        
        # Start a transaction
        self.db_manager.begin_transaction()
        
        # Execute statements in transaction
        self.db_manager.execute(
            "INSERT INTO test_table (name, value) VALUES (?, ?)",
            params=("Rollback Item", 111.1)
        )
        
        # Rollback the transaction
        self.db_manager.rollback()
        
        # Verify results after rollback
        result = self.db_manager.execute("SELECT * FROM test_table ORDER BY id")
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]['name'], "Before Rollback")
    
    def tearDown(self):
        """Clean up after tests."""
        self.db_manager.close()

if __name__ == '__main__':
    unittest.main()
