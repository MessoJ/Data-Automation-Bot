import os
import json
import logging
from datetime import datetime

def load_config(config_path=None):
    """
    Load configuration from a file or environment variables.
    
    Parameters:
    -----------
    config_path : str, optional
        Path to the configuration file
        
    Returns:
    --------
    dict
        Configuration dictionary
    """
    # Default configuration
    default_config = {
        "app_name": "Data Automation Bot",
        "environment": "development",
        "api": {
            "base_url": "https://api.example.com",
            "timeout": 30,
            "retry_attempts": 3,
            "api_key": ""
        },
        "database": {
            "type": "sqlite",
            "connection_string": "data_automation.db",
            "pool_size": 5
        },
        "data_preprocessing": {
            "default_na_values": ["", "NA", "N/A", "null", "None"],
            "default_date_format": "%Y-%m-%d",
            "transformation_rules": {}
        },
        "reporting": {
            "output_directory": "reports",
            "template_directory": "templates",
            "generate_pdf": False,
            "chart_columns": ["value", "count"],
            "distribution_columns": ["value"]
        },
        "scheduler": {
            "num_workers": 2,
            "max_history": 100,
            "jobs": {
                "daily_data_fetch": {
                    "type": "data_fetch",
                    "source_type": "api",
                    "source_config": {
                        "endpoint": "/data",
                        "method": "GET"
                    },
                    "destination_table": "raw_data",
                    "schedule": {
                        "type": "daily",
                        "value": "09:00"
                    }
                },
                "data_processing": {
                    "type": "data_process",
                    "source_table": "raw_data",
                    "destination_table": "processed_data",
                    "operations": [
                        {
                            "type": "clean",
                            "config": {
                                "drop_duplicates": True,
                                "handle_missing": "fill",
                                "fill_value": 0
                            }
                        },
                        {
                            "type": "transform",
                            "config": {
                                "normalize_columns": ["value"]
                            }
                        }
                    ],
                    "schedule": {
                        "type": "daily",
                        "value": "10:00"
                    }
                },
                "daily_report": {
                    "type": "report_generate",
                    "report_type": "daily",
                    "recipients": ["user@example.com"],
                    "schedule": {
                        "type": "daily",
                        "value": "11:00"
                    }
                }
            }
        },
        "logging": {
            "level": "INFO",
            "file": "data_automation.log",
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        }
    }
    
    config = default_config.copy()
    
    # Load from file if specified
    if config_path and os.path.exists(config_path):
        try:
            with open(config_path, 'r') as f:
                file_config = json.load(f)
                # Recursively update default config with file config
                _update_dict(config, file_config)
        except Exception as e:
            logging.error(f"Error loading config from {config_path}: {e}")
    
    # Override with environment variables
    _override_from_env(config)
    
    # Set up logging
    _setup_logging(config)
    
    return config

def _update_dict(d, u):
    """
    Recursively update a dictionary.
    
    Parameters:
    -----------
    d : dict
        Dictionary to update
    u : dict
        Dictionary with updates
        
    Returns:
    --------
    dict
        Updated dictionary
    """
    for k, v in u.items():
        if isinstance(v, dict) and k in d and isinstance(d[k], dict):
            d[k] = _update_dict(d[k], v)
        else:
            d[k] = v
    return d

def _override_from_env(config, prefix="DATA_BOT"):
    """
    Override configuration with environment variables.
    
    Parameters:
    -----------
    config : dict
        Configuration dictionary to update
    prefix : str, optional
        Prefix for environment variables
    """
    for key, value in os.environ.items():
        if key.startswith(prefix + "_"):
            # Remove prefix and split by underscore
            parts = key[len(prefix) + 1:].lower().split("_")
            
            # Navigate the config dictionary
            current = config
            for part in parts[:-1]:
                if part not in current:
                    current[part] = {}
                current = current[part]
            
            # Set the value
            current[parts[-1]] = _parse_env_value(value)

def _parse_env_value(value):
    """
    Parse environment variable values to appropriate types.
    
    Parameters:
    -----------
    value : str
        Environment variable value
        
    Returns:
    --------
    Any
        Parsed value
    """
    # Try to parse as JSON first
    try:
        return json.loads(value)
    except:
        pass
    
    # Parse booleans
    if value.lower() == "true":
        return True
    elif value.lower() == "false":
        return False
    
    # Parse numbers
    try:
        if "." in value:
            return float(value)
        else:
            return int(value)
    except:
        # Return as is if nothing else works
        return value

def _setup_logging(config):
    """
    Set up logging based on configuration.
    
    Parameters:
    -----------
    config : dict
        Configuration dictionary
    """
    log_config = config.get("logging", {})
    log_level = getattr(logging, log_config.get("level", "INFO"))
    log_file = log_config.get("file", "data_automation.log")
    log_format = log_config.get("format", "%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    
    # Create logs directory if it doesn't exist
    log_dir = os.path.dirname(log_file)
    if log_dir and not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    # Configure logging
    logging.basicConfig(
        level=log_level,
        format=log_format,
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()
        ]
    )
