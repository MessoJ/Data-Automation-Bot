"""
Data Transformer for handling data transformation operations.

This module provides functionality to transform cleaned data by:
- Feature engineering
- Data normalization and scaling
- Data aggregation
- Format conversion
"""

import logging
from typing import Dict, List, Any, Union, Optional
import pandas as pd
import numpy as np
from datetime import datetime
import json

from utils.helpers import handle_exceptions

class DataTransformer:
    """Class for transforming cleaned data."""
    
    def __init__(self):
        """Initialize the data transformer."""
        logging.debug("Initializing DataTransformer")
    
    @handle_exceptions
    def transform(self, cleaned_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Transform cleaned data records.
        
        Args:
            cleaned_data: List of cleaned data records to transform.
            
        Returns:
            List of transformed data records.
        """
        if not cleaned_data:
            logging.warning("No data to transform")
            return []
            
        logging.info(f"Transforming {len(cleaned_data)} cleaned data records")
        
        # Convert to pandas DataFrame for easier manipulation
        df = pd.DataFrame(cleaned_data)
        
        # Apply transformation operations
        df = self._engineer_features(df)
        df = self._normalize_and_scale(df)
        df = self._aggregate_data(df)
        df = self._standardize_format(df)
        
        # Convert back to list of dictionaries
        transformed_data = df.to_dict(orient="records")
        
        logging.info(f"Transformation complete. Produced {len(transformed_data)} transformed records")
        return transformed_data
    
    def _engineer_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Create new features based on existing data.
        
        Args:
            df: DataFrame with cleaned data.
            
        Returns:
            DataFrame with new engineered features.
        """
        # Example: Extract date components from timestamp fields
        date_columns = df.select_dtypes(include=['datetime64']).columns
        
        for column in date_columns:
            # Extract useful date components
            df[f"{column}_year"] = df[column].dt.year
            df[f"{column}_month"] = df[column].dt.month
            df[f"{column}_day"] = df[column].dt.day
            df[f"{column}_dayofweek"] = df[column].dt.dayofweek
            
            logging.debug(f"Extracted date components from '{column}'")
        
        # Example: Create categorical features from numeric ranges
        numeric_columns = df.select_dtypes(include=[np.number]).columns
        
        for column in numeric_columns:
            # Skip ID columns and date components we just created
            if column.endswith('_year') or column.endswith('_month') or column.endswith('_day') or column.endswith('_dayofweek'):
                continue
                
            if column.lower().endswith('id') or df[column].nunique() < 10:
                continue
                
            # Create binned categories
            try:
                df[f"{column}_category"] = pd.qcut(df[column], q=4, labels=['low', 'medium_low', 'medium_high', 'high'])
                logging.debug(f"Created categorical bins for '{column}'")
            except:
                # Skip if binning fails (e.g., for columns with too few unique values)
                logging.debug(f"Skipped creating bins for '{column}'")
        
        return df
    
    def _normalize_and_scale(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Normalize and scale numeric features.
        
        Args:
            df: DataFrame with cleaned data.
            
        Returns:
            DataFrame with normalized and scaled features.
        """
        numeric_columns = df.select_dtypes(include=[np.number]).columns
        
        for column in numeric_columns:
            # Skip ID columns, created categories, and date components
            if (column.endswith('_category') or column.endswith('_year') or 
                column.endswith('_month') or column.endswith('_day') or 
                column.endswith('_dayofweek')):
                continue
                
            if column.lower().endswith('id') or df[column].nunique() < 10:
                continue
            
            # Min-max scaling to [0, 1] range
            min_val = df[column].min()
            max_val = df[column].max()
            
            # Avoid division by zero
            if min_val != max_val:
                df[f"{column}_scaled"] = (df[column] - min_val) / (max_val - min_val)
                logging.debug(f"Created min-max scaled version of '{column}'")
            
            # Z-score normalization
            mean_val = df[column].mean()
            std_val = df[column].std()
            
            # Avoid division by zero
            if std_val > 0:
                df[f"{column}_normalized"] = (df[column] - mean_val) / std_val
                logging.debug(f"Created z-score normalized version of '{column}'")
        return df
    
    def _aggregate_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Perform data aggregation operations.
        
        Args:
            df: DataFrame with cleaned data.
            
        Returns:
            DataFrame with aggregated data.
        """
        # Look for columns that might indicate a grouping key
        potential_group_cols = [col for col in df.columns 
                               if any(keyword in col.lower() 
                                     for keyword in ['id', 'type', 'category', 'group'])]
        
        # If we found potential grouping columns
        if potential_group_cols and len(df) > 1:
            # Take the first suitable column for grouping
            group_col = potential_group_cols[0]
            
            # Find numeric columns to aggregate
            numeric_cols = df.select_dtypes(include=[np.number]).columns
            numeric_cols = [col for col in numeric_cols 
                           if not col.endswith(('_normalized', '_scaled', '_category', '_year', '_month', '_day', '_dayofweek'))
                           and not col.lower().endswith('id')]
            
            if numeric_cols:
                # Create aggregation stats
                logging.debug(f"Aggregating data by '{group_col}'")
                
                # Group and aggregate
                grouped = df.groupby(group_col)[numeric_cols].agg(['mean', 'min', 'max', 'std'])
                
                # Flatten column hierarchy
                grouped.columns = [f"{col}_{agg}" for col, agg in grouped.columns]
                
                # Reset index to convert back to regular dataframe
                grouped = grouped.reset_index()
                
                # Merge aggregated data back with original
                df = pd.merge(df, grouped, on=group_col, how='left')
                
                logging.debug(f"Added {len(grouped.columns) - 1} aggregated columns")
        return df
    
    def _standardize_format(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Standardize the output format for downstream processing.
        
        Args:
            df: DataFrame with transformed data.
            
        Returns:
            DataFrame with standardized format.
        """
        # Create a standard metadata column to store additional attributes
        if 'metadata' not in df.columns:
            df['metadata'] = None
        
        # Select columns to include in metadata
        # Include derived columns and keep core columns separate
        derived_cols = [col for col in df.columns 
                       if any(suffix in col 
                             for suffix in ['_normalized', '_scaled', '_category', 
                                           '_year', '_month', '_day', '_dayofweek',
                                           '_mean', '_min', '_max', '_std'])]
        
        # Create a standard structure
        result_df = pd.DataFrame()
        
        # Identify or create key columns
        if 'id' in df.columns:
            result_df['source_id'] = df['id']
        elif 'source_id' in df.columns:
            result_df['source_id'] = df['source_id']
        else:
            # Create a sequential ID if none exists
            result_df['source_id'] = [f"record_{i}" for i in range(len(df))]
        
        # Identify or create data type
        if 'type' in df.columns:
            result_df['data_type'] = df['type']
        elif 'data_type' in df.columns:
            result_df['data_type'] = df['data_type']
        else:
            result_df['data_type'] = 'standard'
        
        # Find a value column or use first numeric column
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        non_derived_numeric = [col for col in numeric_cols 
                              if col not in derived_cols 
                              and not col.lower().endswith('id')]
        
        if 'value' in df.columns:
            result_df['value'] = df['value']
        elif len(non_derived_numeric) > 0:
            result_df['value'] = df[non_derived_numeric[0]]
        else:
            result_df['value'] = 0
        
        # Find or create timestamp
        date_cols = df.select_dtypes(include=['datetime64']).columns
        if 'timestamp' in df.columns:
            result_df['timestamp'] = df['timestamp']
        elif len(date_cols) > 0:
            result_df['timestamp'] = df[date_cols[0]]
        else:
            result_df['timestamp'] = datetime.now()
        
        # Store all other columns in metadata
        result_df['metadata'] = df.apply(
            lambda row: {
                col: row[col] if not pd.isna(row[col]) 
                else None
                for col in df.columns 
                if col not in result_df.columns
            },
            axis=1
        )
        
        # Convert any non-serializable types in metadata
        def fix_non_serializable(obj):
            if isinstance(obj, (np.int64, np.int32, np.int16, np.int8)):
                return int(obj)
            elif isinstance(obj, (np.float64, np.float32, np.float16)):
                return float(obj)
            elif isinstance(obj, (datetime, np.datetime64)):
                return obj.isoformat() if hasattr(obj, 'isoformat') else str(obj)
            elif isinstance(obj, (pd.Timestamp)):
                return obj.isoformat()
            elif isinstance(obj, (np.bool_)):
                return bool(obj)
            elif isinstance(obj, (np.ndarray)):
                return obj.tolist()
            else:
                return obj
        
        # Fix non-serializable types in metadata
        for i, metadata in enumerate(result_df['metadata']):
            if metadata:
                result_df.at[i, 'metadata'] = {
                    k: fix_non_serializable(v) for k, v in metadata.items()
                }
        
        logging.debug(f"Standardized data format: {list(result_df.columns)}")
        return result_df
