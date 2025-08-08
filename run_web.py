#!/usr/bin/env python3
"""
Run the Data Automation Bot Web Application

This script starts the Flask web application that serves both the landing page
and the dashboard interface for the Data Automation Bot.
"""

import os
import sys
import logging
from datetime import datetime

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

def main():
    """Main function to run the web application."""
    try:
        # Ensure essential directories
        os.makedirs("logs", exist_ok=True)
        os.makedirs("reports", exist_ok=True)
        
        # Import and create the Flask app
        from web.app import create_app
        from scheduler.job_scheduler import JobScheduler
        from main import process_data_job
        import config

        app = create_app()

        # Bring up scheduler in background
        try:
            scheduler = JobScheduler()
            scheduler.add_job(
                "data_processing",
                process_data_job,
                trigger='interval',
                seconds=config.SCHEDULER_INTERVAL
            )
            scheduler.start()
            logger.info("Scheduler started with data_processing job")
        except Exception as sch_ex:
            logger.warning(f"Scheduler not started: {sch_ex}")
        
        # Configuration
        host = os.environ.get('HOST', '0.0.0.0')
        port = int(os.environ.get('PORT', 5000))
        debug = os.environ.get('DEBUG', 'True').lower() == 'true'
        
        logger.info("Starting Data Automation Bot Web Application")
        logger.info(f"Landing Page: http://{host}:{port}/")
        logger.info(f"Dashboard: http://{host}:{port}/web/")
        logger.info(f"Debug mode: {debug}")
        logger.info(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Run the application
        app.run(host=host, port=port, debug=debug, threaded=True)
        
    except ImportError as e:
        logger.error(f"Failed to import required modules: {e}")
        logger.info("Please ensure all dependencies are installed:")
        logger.info("pip install -r requirements.txt")
        sys.exit(1)
        
    except Exception as e:
        logger.error(f"Failed to start web application: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
