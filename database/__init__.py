"""
Database module for data automation bot.

This module contains the database manager for storing and retrieving processed data.
"""

from .db_manager import DatabaseManager, ProcessedData, DataSource

__all__ = ['DatabaseManager', 'ProcessedData', 'DataSource']