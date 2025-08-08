"""
Data Cleaner for handling data cleaning operations.

This module provides functionality to clean raw data by:
- Removing duplicates
- Handling missing values
- Filtering outliers
- Normalizing data formats
"""

import logging
from typing import Dict, List, Any, Union, Optional
import pandas as pd
import numpy as np
from datetime import datetime
import re

from utils.helpers import handle_exceptions

class DataCleaner:
    """Class for cleaning raw data."""
    
    def __init__(self):
        """Initialize the data cleaner."""
        logging.debug("Initializing DataCleaner")
    
    @handle_exceptions
    def clean(self, raw_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Clean raw data records.
        
        Args:
            raw_data: List of raw data records to clean.
            
        Returns:
            List of cleaned data records.
        """
        if not raw_data:
            logging.warning("No data to clean")
            return []
            
        logging.info(f"Cleaning {len(raw_data)} raw data records")
        
        # Convert to pandas DataFrame for easier manipulation
        df = pd.DataFrame(raw_data)
        
        # Track original record count
        original_count = len(df)
        
        # Apply cleaning operations
        df = self._remove_duplicates(df)
        df = self._handle_missing_values(df)
        df = self._filter_outliers(df)
        df = self._normalize_formats(df)
        
        # Convert back to list of dictionaries
        cleaned_data = df.to_dict(orient="records")
        
        logging.info(f"Cleaning complete. Reduced from {original_count} to {len(cleaned_data)} records")
        return cleaned_data
    
    def _remove_duplicates(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Remove duplicate records from the dataset.
        
        Args:
            df: DataFrame with raw data.
            
        Returns:
            DataFrame with duplicates removed.
        """
        before_count = len(df)
        
        # Check if there's a unique identifier column
        if "id" in df.columns:
            df = df.drop_duplicates(subset=["id"])
        else:
            # If no ID, use all columns to identify duplicates
            df = df.drop_duplicates()
        
        after_count = len(df)
        if before_count > after_count:
            logging.info(f"Removed {before_count - after_count} duplicate records")
            
        return df
    
    def _handle_missing_values(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Handle missing values in the dataset.
        
        Args:
            df: DataFrame with raw data.
            
        Returns:
            DataFrame with missing values handled.
        """
        # Check for null values
        null_counts = df.isnull().sum()
        if null_counts.sum() > 0:
            logging.info(f"Found {null_counts.sum()} missing values across {sum(null_counts > 0)} columns")
            
            # Handle missing values differently based on column type
            for column in df.columns:
                # Skip columns with no missing values
                if null_counts[column] == 0:
                    continue
                
                # For numeric columns, fill with median
                if np.issubdtype(df[column].dtype, np.number):
                    median_value = df[column].median()
                    df[column] = df[column].fillna(median_value)
                    logging.debug(f"Filled {null_counts[column]} missing values in '{column}' with median {median_value}")
                
                # For categorical/string columns, fill with mode or 'unknown'
                elif df[column].dtype == 'object':
                    # If more than 50% is missing, just use 'unknown'
                    if null_counts[column] / len(df) > 0.5:
                        df[column] = df[column].fillna("unknown")
                    else:
                        # Use most common value
                        mode_value = df[column].mode()[0]
                        df[column] = df[column].fillna(mode_value)
                    logging.debug(f"Filled {null_counts[column]} missing values in '{column}'")
                
                # For datetime columns, use previous value or current time
                elif pd.api.types.is_datetime64_any_dtype(df[column]):
                    df[column] = df[column].fillna(method='ffill')
                    # If still have NAs at the beginning, use current time
                    df[column] = df[column].fillna(datetime.now())
                    logging.debug(f"Filled {null_counts[column]} missing datetime values in '{column}'")
        
        return df
    
    def _filter_outliers(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Filter outliers from numeric columns using IQR method.
        
        Args:
            df: DataFrame with raw data.
            
        Returns:
            DataFrame with outliers handled.
        """
        numeric_columns = df.select_dtypes(include=[np.number]).columns
        
        for column in numeric_columns:
            # Skip columns that are IDs or categorical
            if column.lower().endswith('id') or df[column].nunique() < 10:
                continue
                
            # Calculate IQR
            Q1 = df[column].quantile(0.25)
            Q3 = df[column].quantile(0.75)
            IQR = Q3 - Q1
            
            # Define bounds
            lower_bound = Q1 - 3 * IQR
            upper_bound = Q3 + 3 * IQR
            
            # Identify outliers
            outliers = df[(df[column] < lower_bound) | (df[column] > upper_bound)]
            
            if not outliers.empty:
                logging.info(f"Found {len(outliers)} outliers in column '{column}'")
                
                # Clip values to the bounds instead of removing rows
                df[column] = df[column].clip(lower=lower_bound, upper=upper_bound)
                logging.debug(f"Clipped outliers in '{column}' to range [{lower_bound:.2f}, {upper_bound:.2f}]")
        
        return df
    
    def _normalize_formats(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Normalize data formats for consistency.
        
        Args:
            df: DataFrame with raw data.
            
        Returns:
            DataFrame with normalized formats.
        """
        # Normalize string columns by removing extra whitespace and standardizing case
        string_columns = df.select_dtypes(include=['object']).columns
        
        for column in string_columns:
            # Skip columns that appear to contain JSON or complex data
            # Use regex=False to avoid invalid regex for characters like '['
            try:
                has_brace = df[column].str.contains('{', regex=False).any()
                has_bracket = df[column].str.contains('[', regex=False).any()
            except Exception:
                has_brace = False
                has_bracket = False
            if has_brace or has_bracket:
                continue
                
            # Strip whitespace and standardize case
            df[column] = df[column].str.strip()
            
            # If the column name suggests it's a category or type, standardize case
            if any(keyword in column.lower() for keyword in ['type', 'category', 'status', 'level']):
                df[column] = df[column].str.lower()
        
        # Convert date strings to datetime objects
        for column in df.columns:
            if any(keyword in column.lower() for keyword in ['date', 'time', 'created', 'updated']):
                if df[column].dtype == 'object':
                    try:
                        df[column] = pd.to_datetime(df[column], errors='coerce')
                        logging.debug(f"Converted '{column}' to datetime format")
                    except:
                        logging.debug(f"Failed to convert '{column}' to datetime")
        
        return df
