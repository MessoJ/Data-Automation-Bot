"""
Web application module for Data Automation Bot.

This module provides a Flask-based web interface for monitoring and managing
the data automation bot, including dashboard, reports, and job management.
"""

from .app import create_app

__all__ = ['create_app']