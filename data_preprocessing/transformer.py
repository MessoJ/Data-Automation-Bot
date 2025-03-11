import pandas as pd
import numpy as np
import logging
from sklearn.preprocessing import StandardScaler, MinMaxScaler, OneHotEncoder
from sklearn.impute import SimpleImputer

logger = logging.getLogger(__name__)

class DataTransformer:
    """
    Class for transforming cleaned data into a format suitable for analysis and reporting.
    Handles feature engineering, normalization, encoding, etc.
    """
    
    def __init__(self, config=None):
        """
        Initialize the DataTransformer with optional configuration.
        
        Args:
            config (dict, optional): Configuration options for transformation.
        """
        self.config = config or {}
        self.encoders = {}
        self.scalers = {}
        logger.info("DataTransformer initialized")
    
    def transform_dataframe(self, df, transformations=None):
        """
        Transform a pandas DataFrame using specified transformations.
        
        Args:
            df (pd.DataFrame): The DataFrame to transform.
            transformations (dict, optional): Transformation strategies to apply.
                Example: {'normalize': ['col1', 'col2'], 'encode': ['col3']}
        
        Returns:
            pd.DataFrame: The transformed DataFrame.
        """
        if df.empty:
            logger.warning("Empty DataFrame provided for transformation")
            return df
        
        transformations = transformations or {}
        
        logger.info(f"Transforming DataFrame with shape {df.shape}")
        
        # Make a copy to avoid modifying the original
        transformed_df = df.copy()
        
        # Apply transformations
        if 'normalize' in transformations:
            transformed_df = self._normalize_columns(
                transformed_df, 
                transformations['normalize']
            )
        
        if 'encode' in transformations:
            transformed_df = self._encode_categorical(
                transformed_df, 
                transformations['encode']
            )
        
        if 'date_features' in transformations:
            transformed_df = self._extract_date_features(
                transformed_df, 
                transformations['date_features']
            )
        
        if 'custom' in transformations:
            for custom_transform in transformations['custom']:
                transformed_df = custom_transform(transformed_df)
        
        logger.info(f"Transformation complete. Resulting shape: {transformed_df.shape}")
        return transformed_df
    
    def _normalize_columns(self, df, columns, method='standard'):
        """
        Normalize numeric columns.
        
        Args:
            df (pd.DataFrame): The DataFrame to process.
            columns (list): List of columns to normalize.
            method (str): Normalization method ('standard', 'minmax').
        
        Returns:
            pd.DataFrame: DataFrame with normalized columns.
        """
        # Filter to only include numeric columns that exist in the dataframe
        numeric_cols = df.select_dtypes(include=['number']).columns
        columns_to_normalize = [col for col in columns if col in numeric_cols]
        
        if not columns_to_normalize:
            logger.warning("No valid numeric columns provided for normalization")
            return df
        
        logger.info(f"Normalizing columns: {columns_to_normalize} using {method} method")
        
        # Select the appropriate scaler
        if method == 'standard':
            for col in columns_to_normalize:
                if col not in self.scalers:
                    self.scalers[col] = StandardScaler()
                    df[col] = self.scalers[col].fit_transform(df[[col]])
                else:
                    df[col] = self.scalers[col].transform(df[[col]])
        elif method == 'minmax':
            for col in columns_to_normalize:
                if col not in self.scalers:
                    self.scalers[col] = MinMaxScaler()
                    df[col] = self.scalers[col].fit_transform(df[[col]])
                else:
                    df[col] = self.scalers[col].transform(df[[col]])
        
        return df
    
    def _encode_categorical(self, df, columns, method='onehot'):
        """
        Encode categorical columns.
        
        Args:
            df (pd.DataFrame): The DataFrame to process.
            columns (list): List of categorical columns to encode.
            method (str): Encoding method ('onehot', 'label', 'ordinal').
        
        Returns:
            pd.DataFrame: DataFrame with encoded columns.
        """
        # Check that columns exist in the dataframe
        columns_to_encode = [col for col in columns if col in df.columns]
        
        if not columns_to_encode:
            logger.warning("No valid categorical columns provided for encoding")
            return df
        
        logger.info(f"Encoding columns: {columns_to_encode} using {method} method")
        
        if method == 'onehot':
            for col in columns_to_encode:
                if col not in self.encoders:
                    self.encoders[col] = OneHotEncoder(sparse_output=False, handle_unknown='ignore')
                    encoded = self.encoders[col].fit_transform(df[[col]])
                else:
                    encoded = self.encoders[col].transform(df[[col]])
                
                # Create column names for the encoded features
                encoded_cols = [f"{col}_{cat}" for cat in self.encoders[col].categories_[0]]
                
                # Add the encoded columns to the dataframe
                encoded_df = pd.DataFrame(encoded, columns=encoded_cols, index=df.index)
                df = pd.concat([df, encoded_df], axis=1)
                
                # Drop the original column
                df = df.drop(columns=[col])
        
        elif method == 'label':
            for col in columns_to_encode:
                # For label encoding, we'll just convert categories to integers
                df[col] = pd.Categorical(df[col]).codes
        
        return df
    
    def _extract_date_features(self, df, date_columns):
        """
        Extract useful features from date columns.
        
        Args:
            df (pd.DataFrame): The DataFrame to process.
            date_columns (list): List of date columns to process.
        
        Returns:
            pd.DataFrame: DataFrame with extracted date features.
        """
        for col in date_columns:
            if col not in df.columns:
                logger.warning(f"Date column '{col}' not found in DataFrame")
                continue
            
            logger.info(f"Extracting date features from column '{col}'")
            
            # Try to convert to datetime if not already
            if not pd.api.types.is_datetime64_dtype(df[col]):
                try:
                    df[col] = pd.to_datetime(df[col])
                except:
                    logger.warning(f"Failed to convert column '{col}' to datetime")
                    continue
            
            # Extract date components
            df[f"{col}_year"] = df[col].dt.year
            df[f"{col}_month"] = df[col].dt.month
            df[f"{col}_day"] = df[col].dt.day
            df[f"{col}_dayofweek"] = df[col].dt.dayofweek
            df[f"{col}_quarter"] = df[col].dt.quarter
            
            # Create is_weekend feature
            df[f"{col}_is_weekend"] = df[col].dt.dayofweek >= 5
        
        return df
    
    def add_aggregations(self, df, group_by, agg_columns, agg_functions=None):
        """
        Add aggregated features to the DataFrame.
        
        Args:
            df (pd.DataFrame): The DataFrame to process.
            group_by (str or list): Column(s) to group by.
            agg_columns (list): Columns to aggregate.
            agg_functions (dict, optional): Aggregation functions to apply.
                Default: {'mean', 'sum', 'min', 'max'}
        
        Returns:
            pd.DataFrame: DataFrame with added aggregation features.
        """
        if isinstance(group_by, str):
            group_by = [group_by]
            
        agg_functions = agg_functions or ['mean', 'sum', 'min', 'max']
        
        logger.info(f"Adding aggregations grouping by {group_by}")
        
        # Create aggregations
        agg_dict = {col: agg_functions for col in agg_columns}
        aggregated = df.groupby(group_by).agg(agg_dict)
        
        # Flatten the column names
        aggregated.columns = [f"{col}_{func}" for col, func in 
                             zip(aggregated.columns.get_level_values(0),
                                 aggregated.columns.get_level_values(1))]
        
        # Reset index to make it joinable
        aggregated = aggregated.reset_index()
        
        # Merge aggregations back to the original dataframe
        df = df.merge(aggregated, on=group_by, how='left')
        
        logger.info(f"Added {len(aggregated.columns) - len(group_by)} aggregation features")
        return df
    
    def create_interactions(self, df, interaction_pairs):
        """
        Create interaction features between pairs of columns.
        
        Args:
            df (pd.DataFrame): The DataFrame to process.
            interaction_pairs (list of tuples): Pairs of columns to create interactions for.
        
        Returns:
            pd.DataFrame: DataFrame with added interaction features.
        """
        logger.info(f"Creating {len(interaction_pairs)} interaction features")
        
        for col1, col2 in interaction_pairs:
            if col1 not in df.columns or col2 not in df.columns:
                logger.warning(f"Can't create interaction: column '{col1}' or '{col2}' not found")
                continue
                
            # Only create interactions for numeric columns
            if not (pd.api.types.is_numeric_dtype(df[col1]) and 
                    pd.api.types.is_numeric_dtype(df[col2])):
                logger.warning(f"Can't create interaction: columns must be numeric")
                continue
                
            # Create the interaction (multiplication)
            df[f"{col1}_x_{col2}"] = df[col1] * df[col2]
            
        return df
