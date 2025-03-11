import os
import logging
import json
from datetime import datetime
import hashlib
import re
import pandas as pd

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("data_automation.log"),
        logging.StreamHandler()
    ]
)

def ensure_directory_exists(directory_path):
    """
    Create a directory if it doesn't exist.
    
    Parameters:
    -----------
    directory_path : str
        Path to the directory to check/create
    """
    if not os.path.exists(directory_path):
        os.makedirs(directory_path)
        logging.info(f"Created directory: {directory_path}")

def get_file_hash(file_path):
    """
    Generate a hash for a file to check if it has changed.
    
    Parameters:
    -----------
    file_path : str
        Path to the file
        
    Returns:
    --------
    str
        MD5 hash of the file
    """
    hash_md5 = hashlib.md5()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()

def load_json(file_path):
    """
    Load data from a JSON file.
    
    Parameters:
    -----------
    file_path : str
        Path to the JSON file
        
    Returns:
    --------
    dict
        Loaded JSON data as a dictionary
    """
    try:
        with open(file_path, 'r') as f:
            return json.load(f)
    except (json.JSONDecodeError, FileNotFoundError) as e:
        logging.error(f"Error loading JSON file {file_path}: {e}")
        return {}

def save_json(data, file_path):
    """
    Save data to a JSON file.
    
    Parameters:
    -----------
    data : dict
        Data to save
    file_path : str
        Path to the JSON file
    """
    try:
        with open(file_path, 'w') as f:
            json.dump(data, f, indent=4)
    except Exception as e:
        logging.error(f"Error saving JSON file {file_path}: {e}")

def validate_email(email):
    """
    Validate an email address format.
    
    Parameters:
    -----------
    email : str
        Email address to validate
        
    Returns:
    --------
    bool
        True if the email format is valid, False otherwise
    """
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(email_pattern, email))

def format_timestamp(timestamp=None, format_str="%Y-%m-%d %H:%M:%S"):
    """
    Format a timestamp or current time.
    
    Parameters:
    -----------
    timestamp : datetime, optional
        Timestamp to format. Default is current time.
    format_str : str, optional
        Format string. Default is "%Y-%m-%d %H:%M:%S".
        
    Returns:
    --------
    str
        Formatted timestamp
    """
    if timestamp is None:
        timestamp = datetime.now()
    return timestamp.strftime(format_str)

def retry_operation(operation, max_attempts=3, delay=5):
    """
    Retry an operation multiple times before giving up.
    
    Parameters:
    -----------
    operation : callable
        Function to execute
    max_attempts : int, optional
        Maximum number of retry attempts. Default is 3.
    delay : int, optional
        Delay between attempts in seconds. Default is 5.
        
    Returns:
    --------
    Any
        Result of the operation if successful
        
    Raises:
    -------
    Exception
        The last exception encountered if all attempts fail
    """
    import time
    attempts = 0
    last_exception = None
    
    while attempts < max_attempts:
        try:
            return operation()
        except Exception as e:
            attempts += 1
            last_exception = e
            logging.warning(f"Operation failed (attempt {attempts}/{max_attempts}): {e}")
            if attempts < max_attempts:
                time.sleep(delay)
    
    if last_exception:
        logging.error(f"Operation failed after {max_attempts} attempts: {last_exception}")
        raise last_exception

def chunker(seq, size):
    """
    Split a sequence into chunks of the specified size.
    
    Parameters:
    -----------
    seq : iterable
        Sequence to split
    size : int
        Size of each chunk
        
    Returns:
    --------
    generator
        Generator yielding chunks of the sequence
    """
    return (seq[pos:pos + size] for pos in range(0, len(seq), size))

def detect_file_type(file_path):
    """
    Detect the type of a file based on its extension.
    
    Parameters:
    -----------
    file_path : str
        Path to the file
        
    Returns:
    --------
    str
        File type (csv, excel, json, etc.)
    """
    extension = file_path.lower().split('.')[-1]
    
    if extension in ['csv']:
        return 'csv'
    elif extension in ['xls', 'xlsx', 'xlsm']:
        return 'excel'
    elif extension in ['json']:
        return 'json'
    elif extension in ['txt']:
        return 'text'
    elif extension in ['xml']:
        return 'xml'
    else:
        return 'unknown'

def read_data_file(file_path):
    """
    Read data from various file types into a pandas DataFrame.
    
    Parameters:
    -----------
    file_path : str
        Path to the data file
        
    Returns:
    --------
    pandas.DataFrame
        Data from the file
    """
    file_type = detect_file_type(file_path)
    
    try:
        if file_type == 'csv':
            return pd.read_csv(file_path)
        elif file_type == 'excel':
            return pd.read_excel(file_path)
        elif file_type == 'json':
            return pd.read_json(file_path)
        elif file_type == 'text':
            return pd.read_csv(file_path, delimiter='\t')
        elif file_type == 'xml':
            return pd.read_xml(file_path)
        else:
            logging.error(f"Unsupported file type for {file_path}")
            return pd.DataFrame()
    except Exception as e:
        logging.error(f"Error reading file {file_path}: {e}")
        return pd.DataFrame()
