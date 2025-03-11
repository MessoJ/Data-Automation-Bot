"""
Tests for the data preprocessing module.
"""
import unittest
import pandas as pd
import numpy as np
from unittest.mock import patch
from data_automation_bot.data_preprocessing.cleaner import DataCleaner
from data_automation_bot.data_preprocessing.transformer import DataTransformer

class TestDataCleaner(unittest.TestCase):
    """Test cases for the DataCleaner class."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create a DataCleaner instance
        self.cleaner = DataCleaner()
        
        # Create sample test data
        self.sample_df = pd.DataFrame({
            'id': [1, 2, 3, 4, 5],
            'name': ['Product A', 'Product B', None, 'Product D', 'Product E'],
            'price': [10.5, 20.0, 15.75, None, 25.5],
            'category': ['Electronics', 'Books', 'Electronics', 'Clothing', None],
            'in_stock': ['Yes', 'No', 'Yes', 'Invalid', np.nan],
            'date_added': ['2023-01-01', '2023-01-02', 'invalid date', '2023-01-04', '2023-01-05']
        })
    
    def test_remove_duplicates(self):
        """Test removing duplicate rows."""
        # Create a DataFrame with duplicates
        df_with_duplicates = pd.concat([self.sample_df, self.sample_df.iloc[0:2]], ignore_index=True)
        
        # Remove duplicates
        result_df = self.cleaner.remove_duplicates(df_with_duplicates)
        
        # Verify duplicates were removed
        self.assertEqual(len(result_df), len(self.sample_df))
    
    def test_handle_missing_values(self):
        """Test handling missing values."""
        # Handle missing values with different strategies
        result_df = self.cleaner.handle_missing_values(
            self.sample_df,
            strategies={
                'name': 'fill',
                'price': 'mean',
                'category': 'mode',
                'in_stock': 'drop',
                'date_added': 'fill'
            },
            fill_values={
                'name': 'Unknown Product',
                'date_added': '2023-01-01'
            }
        )
        
        # Verify results
        self.assertFalse(result_df['name'].isna().any())
        self.assertFalse(result_df['price'].isna().any())
        self.assertFalse(result_df['category'].isna().any())
        
        # Check if name was filled correctly
        self.assertEqual(result_df.loc[2, 'name'], 'Unknown Product')
        
        # Check if price was filled with mean
        mean_price = self.sample_df['price'].mean()
        self.assertAlmostEqual(result_df.loc[3, 'price'], mean_price)
    
    def test_validate_data_types(self):
        """Test validating and converting data types."""
        # Convert data types
        result_df = self.cleaner.validate_data_types(
            self.sample_df,
            {
                'id': 'int',
                'name': 'str',
                'price': 'float',
                'category': 'str',
                'in_stock': 'bool',
                'date_added': 'datetime'
            },
            date_format='%Y-%m-%d'
        )
        
        # Verify data types
        self.assertEqual(result_df['id'].dtype, np.dtype('int'))
        self.assertEqual(result_df['price'].dtype, np.dtype('float'))
        
        # Check boolean conversion
        self.assertTrue(result_df.loc[0, 'in_stock'])
        self.assertFalse(result_df.loc[1, 'in_stock'])
        
        # Check date conversion
        self.assertTrue(pd.api.types.is_datetime64_dtype(result_df['date_added']))
    
    def test_remove_outliers(self):
        """Test outlier removal."""
        # Create DataFrame with outliers
        df_with_outliers = pd.DataFrame({
            'values': [10, 12, 11, 13, 15, 100, 9, 11, 14, 200]
        })
        
        # Remove outliers using z-score method
        result_df = self.cleaner.remove_outliers(df_with_outliers, columns=['values'], method='z-score', threshold=2)
        
        # Verify outliers were removed
        self.assertLess(len(result_df), len(df_with_outliers))
        self.assertNotIn(100, result_df['values'].values)
        self.assertNotIn(200, result_df['values'].values)
    
    def test_standardize_text(self):
        """Test standardizing text columns."""
        # Create DataFrame with text to standardize
        df = pd.DataFrame({
            'product': ['laptop COMPUTER', '  Smartphone ', 'TABLET device', 'desktop PC  ']
        })
        
        # Standardize text
        result_df = self.cleaner.standardize_text(df, columns=['product'])
        
        # Verify results
        self.assertEqual(result_df.loc[0, 'product'], 'laptop computer')
        self.assertEqual(result_df.loc[1, 'product'], 'smartphone')
        self.assertEqual(result_df.loc[2, 'product'], 'tablet device')
        self.assertEqual(result_df.loc[3, 'product'], 'desktop pc')


class TestDataTransformer(unittest.TestCase):
    """Test cases for the DataTransformer class."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create a DataTransformer instance
        self.transformer = DataTransformer()
        
        # Create sample test data
        self.sample_df = pd.DataFrame({
            'id': [1, 2, 3, 4, 5],
            'first_name': ['John', 'Jane', 'Mike', 'Emily', 'David'],
            'last_name': ['Smith', 'Doe', 'Johnson', 'Wilson', 'Brown'],
            'age': [25, 30, 45, 35, 28],
            'salary': [50000, 60000, 75000, 65000, 55000],
            'department': ['Sales', 'IT', 'HR', 'IT', 'Sales'],
            'hire_date': ['2020-01-15', '2019-05-20', '2015-10-30', '2018-03-10', '2021-07-05']
        })
    
    def test_create_feature(self):
        """Test creating new features."""
        # Create new features
        result_df = self.transformer.create_feature(
            self.sample_df,
            features={
                'full_name': lambda df: df['first_name'] + ' ' + df['last_name'],
                'salary_category': lambda df: pd.cut(df['salary'], 
                                                    bins=[0, 55000, 70000, float('inf')],
                                                    labels=['Low', 'Medium', 'High'])
            }
        )
        
        # Verify new features
        self.assertTrue('full_name' in result_df.columns)
        self.assertTrue('salary_category' in result_df.columns)
        
        # Check values
        self.assertEqual(result_df.loc[0, 'full_name'], 'John Smith')
        self.assertEqual(result_df.loc[0, 'salary_category'], 'Low')
        self.assertEqual(result_df.loc[2,
