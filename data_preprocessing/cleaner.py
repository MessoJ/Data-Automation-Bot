import pandas as pd
import numpy as np
import logging

logger = logging.getLogger(__name__)

class DataCleaner:
    """
    Class for cleaning raw data from various sources.
    Handles common preprocessing tasks like handling missing values,
    removing duplicates, fixing data types, etc.
    """
    
    def __init__(self, config=None):
        """
        Initialize the DataCleaner with optional configuration.
        
        Args:
            config (dict, optional): Configuration options for cleaning.
        """
        self.config = config or {}
        logger.info("DataCleaner initialized")
    
    def clean_dataframe(self, df, strategies=None):
        """
        Clean a pandas DataFrame using specified strategies.
        
        Args:
            df (pd.DataFrame): The DataFrame to clean.
            strategies (dict, optional): Cleaning strategies to apply.
                Example: {'missing_values': 'drop', 'duplicates': 'remove'}
        
        Returns:
            pd.DataFrame: The cleaned DataFrame.
        """
        if df.empty:
            logger.warning("Empty DataFrame provided for cleaning")
            return df
        
        strategies = strategies or {
            'missing_values': 'impute_mean',
            'duplicates': 'remove',
            'outliers': 'clip',
            'data_types': 'auto_convert'
        }
        
        logger.info(f"Cleaning DataFrame with shape {df.shape}")
        
        # Make a copy to avoid modifying the original
        cleaned_df = df.copy()
        
        # Handle missing values
        if strategies.get('missing_values') == 'drop':
            cleaned_df = self._drop_missing_values(cleaned_df)
        elif strategies.get('missing_values') == 'impute_mean':
            cleaned_df = self._impute_missing_values(cleaned_df, method='mean')
        elif strategies.get('missing_values') == 'impute_median':
            cleaned_df = self._impute_missing_values(cleaned_df, method='median')
        
        # Handle duplicates
        if strategies.get('duplicates') == 'remove':
            cleaned_df = self._remove_duplicates(cleaned_df)
        
        # Handle outliers
        if strategies.get('outliers') == 'clip':
            cleaned_df = self._clip_outliers(cleaned_df)
        elif strategies.get('outliers') == 'remove':
            cleaned_df = self._remove_outliers(cleaned_df)
        
        # Convert data types
        if strategies.get('data_types') == 'auto_convert':
            cleaned_df = self._convert_data_types(cleaned_df)
        
        logger.info(f"Cleaning complete. Resulting shape: {cleaned_df.shape}")
        return cleaned_df
    
    def _drop_missing_values(self, df, threshold=0.5):
        """
        Drop rows or columns with too many missing values.
        
        Args:
            df (pd.DataFrame): The DataFrame to process.
            threshold (float): The threshold for dropping (default 0.5).
                Rows/columns with more than this fraction of missing values will be dropped.
        
        Returns:
            pd.DataFrame: DataFrame with missing values dropped.
        """
        # Drop columns with too many missing values
        cols_to_drop = df.columns[df.isnull().mean() > threshold]
        if len(cols_to_drop) > 0:
            logger.info(f"Dropping {len(cols_to_drop)} columns with >50% missing values")
            df = df.drop(columns=cols_to_drop)
        
        # Drop rows with too many missing values
        rows_before = len(df)
        df = df.dropna(thresh=int(df.shape[1] * (1 - threshold)))
        rows_dropped = rows_before - len(df)
        if rows_dropped > 0:
            logger.info(f"Dropped {rows_dropped} rows with >50% missing values")
        
        return df
    
    def _impute_missing_values(self, df, method='mean'):
        """
        Impute missing values in the DataFrame.
        
        Args:
            df (pd.DataFrame): The DataFrame to process.
            method (str): Method for imputation ('mean', 'median', 'mode').
        
        Returns:
            pd.DataFrame: DataFrame with imputed values.
        """
        # For each column, impute values based on data type and method
        for col in df.columns:
            missing_count = df[col].isnull().sum()
            
            if missing_count == 0:
                continue
                
            logger.info(f"Imputing {missing_count} missing values in column '{col}'")
            
            # Skip non-numeric columns unless using mode
            if not pd.api.types.is_numeric_dtype(df[col]) and method != 'mode':
                logger.info(f"Skipping non-numeric column '{col}' for {method} imputation")
                continue
            
            if method == 'mean':
                df[col] = df[col].fillna(df[col].mean())
            elif method == 'median':
                df[col] = df[col].fillna(df[col].median())
            elif method == 'mode':
                df[col] = df[col].fillna(df[col].mode()[0] if not df[col].mode().empty else np.nan)
        
        return df
    
    def _remove_duplicates(self, df):
        """
        Remove duplicate rows from the DataFrame.
        
        Args:
            df (pd.DataFrame): The DataFrame to process.
        
        Returns:
            pd.DataFrame: DataFrame with duplicates removed.
        """
        rows_before = len(df)
        df = df.drop_duplicates()
        rows_dropped = rows_before - len(df)
        
        if rows_dropped > 0:
            logger.info(f"Removed {rows_dropped} duplicate rows")
        
        return df
    
    def _clip_outliers(self, df, std_dev=3):
        """
        Clip outliers in numeric columns to be within a certain number of 
        standard deviations from the mean.
        
        Args:
            df (pd.DataFrame): The DataFrame to process.
            std_dev (int): Number of standard deviations to use as threshold.
        
        Returns:
            pd.DataFrame: DataFrame with outliers clipped.
        """
        for col in df.select_dtypes(include=['number']).columns:
            mean = df[col].mean()
            std = df[col].std()
            
            lower_bound = mean - std_dev * std
            upper_bound = mean + std_dev * std
            
            outliers = ((df[col] < lower_bound) | (df[col] > upper_bound)).sum()
            if outliers > 0:
                logger.info(f"Clipping {outliers} outliers in column '{col}'")
                df[col] = df[col].clip(lower=lower_bound, upper=upper_bound)
        
        return df
    
    def _remove_outliers(self, df, std_dev=3):
        """
        Remove rows with outlier values.
        
        Args:
            df (pd.DataFrame): The DataFrame to process.
            std_dev (int): Number of standard deviations to use as threshold.
        
        Returns:
            pd.DataFrame: DataFrame with outlier rows removed.
        """
        mask = pd.Series(True, index=df.index)
        
        for col in df.select_dtypes(include=['number']).columns:
            mean = df[col].mean()
            std = df[col].std()
            
            lower_bound = mean - std_dev * std
            upper_bound = mean + std_dev * std
            
            col_mask = (df[col] >= lower_bound) & (df[col] <= upper_bound)
            outliers = (~col_mask).sum()
            
            if outliers > 0:
                logger.info(f"Found {outliers} outliers in column '{col}'")
                mask = mask & col_mask
        
        rows_before = len(df)
        df = df[mask]
        rows_removed = rows_before - len(df)
        
        if rows_removed > 0:
            logger.info(f"Removed {rows_removed} rows with outlier values")
        
        return df
    
    def _convert_data_types(self, df):
        """
        Automatically convert data types to more appropriate ones.
        
        Args:
            df (pd.DataFrame): The DataFrame to process.
        
        Returns:
            pd.DataFrame: DataFrame with converted data types.
        """
        # Try to convert object columns to numeric where possible
        for col in df.select_dtypes(include=['object']).columns:
            # Try to convert to numeric
            try:
                numeric_col = pd.to_numeric(df[col])
                df[col] = numeric_col
                logger.info(f"Converted column '{col}' to numeric type")
            except:
                # Try to convert to datetime
                try:
                    date_col = pd.to_datetime(df[col])
                    df[col] = date_col
                    logger.info(f"Converted column '{col}' to datetime type")
                except:
                    pass  # Keep as object if conversion fails
        
        return df
