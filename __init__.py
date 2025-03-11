"""
Data Automation Bot

A Python package for automating data collection, processing, and reporting.
"""

__version__ = '1.0.0'

# Import main components for easy access
from .config import load_config
from .scheduler.job_scheduler import JobScheduler
from .api.api_client import APIClient
from .database.db_manager import DatabaseManager
from .data_preprocessing.cleaner import DataCleaner
from .data_preprocessing.transformer import DataTransformer
from .reporting.report_generator import ReportGenerator
