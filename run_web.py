#!/usr/bin/env python3
"""
Web application entry point for Data Automation Bot.

This script starts the Flask web application with the data automation bot backend.
"""

import os
import sys
import logging
from pathlib import Path

import sys
import logging
from pathlib import Path

# Import config BEFORE using it!
import config

log_dir = os.path.dirname(config.LOG_FILE)
if log_dir and not os.path.exists(log_dir):
    os.makedirs(log_dir)

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Import bot components and web app
try:
    from web.app import create_app
    from scheduler.job_scheduler import JobScheduler
    from main import process_data_job
except ImportError as e:
    print(f"Error importing modules: {e}")
    print("Please ensure all dependencies are installed: pip install -r requirements.txt")
    sys.exit(1)

def main():
    """Main function to start the web application."""
    # Setup logging
    logging.basicConfig(
        level=getattr(logging, config.LOG_LEVEL),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(config.LOG_FILE) if hasattr(config, 'LOG_FILE') else logging.StreamHandler(),
            logging.StreamHandler()
        ]
    )
    
    logger = logging.getLogger(__name__)
    logger.info("Starting Data Automation Bot Web Application")
    
    # Create necessary directories
    os.makedirs(config.REPORT_OUTPUT_DIR, exist_ok=True)
    os.makedirs(os.path.dirname(config.LOG_FILE) if hasattr(config, 'LOG_FILE') else './logs', exist_ok=True)
    
    # Initialize and start the job scheduler in the background
    try:
        scheduler = JobScheduler()
        
        # Add the main data processing job
        scheduler.add_job(
            "data_processing",
            process_data_job,
            trigger='interval',
            seconds=config.SCHEDULER_INTERVAL
        )
        
        # Start the scheduler
        scheduler.start()
        logger.info("Job scheduler started successfully")
        
    except Exception as e:
        logger.error(f"Failed to start job scheduler: {e}")
        # Continue without scheduler - web interface will still work
    
    # Create and configure Flask app
    app = create_app()
    
    # Get configuration from environment or use defaults
    host = os.getenv('FLASK_HOST', '0.0.0.0')
    port = int(os.getenv('FLASK_PORT', 5000))
    debug = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
    
    logger.info(f"Starting web server on {host}:{port}")
    logger.info(f"Debug mode: {debug}")
    logger.info(f"Dashboard URL: http://{host}:{port}")
    
    try:
        # Start the Flask application
        app.run(
            host=host,
            port=port,
            debug=debug,
            threaded=True  # Enable threading for better performance
        )
    except KeyboardInterrupt:
        logger.info("Received shutdown signal")
    except Exception as e:
        logger.error(f"Error starting web server: {e}")
        sys.exit(1)
    finally:
        # Cleanup
        try:
            if 'scheduler' in locals():
                scheduler.shutdown()
                logger.info("Job scheduler stopped")
        except:
            pass
        
        logger.info("Data Automation Bot Web Application stopped")

if __name__ == '__main__':
    main()
