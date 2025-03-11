"""
Configuration settings for the Data Automation Bot.

This module contains all configuration parameters including:
- API credentials and endpoints
- Database connection settings
- Scheduling parameters
- Reporting configurations
"""

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# API Settings
API_BASE_URL = os.getenv("API_BASE_URL", "https://api.example.com/v1")
API_KEY = os.getenv("API_KEY", "")
API_TIMEOUT = int(os.getenv("API_TIMEOUT", "30"))

# Database Settings
DB_HOST = os.getenv("DB_HOST", "database-1.cxwa0k264rkw.eu-north-1.rds.amazonaws.com")
DB_PORT = int(os.getenv("DB_PORT", "5432"))
DB_NAME = os.getenv("DB_NAME", "pybot")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("Minaa.2030", "")
DB_CONN_STRING = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# Data Processing Settings
DATA_BATCH_SIZE = int(os.getenv("DATA_BATCH_SIZE", "1000"))
PREPROCESSING_THREADS = int(os.getenv("PREPROCESSING_THREADS", "4"))

# Scheduler Settings
SCHEDULER_INTERVAL = int(os.getenv("SCHEDULER_INTERVAL", "3600"))  # In seconds
RETRY_ATTEMPTS = int(os.getenv("RETRY_ATTEMPTS", "3"))
RETRY_DELAY = int(os.getenv("RETRY_DELAY", "300"))  # In seconds

# Reporting Settings
REPORT_OUTPUT_DIR = os.getenv("REPORT_OUTPUT_DIR", "./reports")
DEFAULT_REPORT_FORMAT = os.getenv("DEFAULT_REPORT_FORMAT", "csv")
REPORT_DATE_FORMAT = os.getenv("REPORT_DATE_FORMAT", "%Y-%m-%d")

# Logging Settings
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_FILE = os.getenv("LOG_FILE", "./logs/data_automation.log")
