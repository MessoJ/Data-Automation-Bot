"""
Main entry point for the Data Automation Bot.

This script initializes the bot components and runs the main workflow:
1. Set up the scheduler
2. Register data processing jobs
3. Start the scheduler to execute jobs based on defined intervals
"""

import logging
import sys
import time
from datetime import datetime

from data_automation_bot.api.api_client import APIClient
from data_automation_bot.database.db_manager import DatabaseManager
from data_automation_bot.data_preprocessing.cleaner import DataCleaner
from data_automation_bot.data_preprocessing.transformer import DataTransformer
from data_automation_bot.reporting.report_generator import ReportGenerator
from data_automation_bot.scheduler.job_scheduler import JobScheduler
from data_automation_bot.utils.helpers import setup_logging
import data_automation_bot.config as config

def process_data_job():
    """Main data processing workflow"""
    logging.info(f"Starting data processing job at {datetime.now()}")
    
    try:
        # Initialize components
        api_client = APIClient()
        db_manager = DatabaseManager()
        data_cleaner = DataCleaner()
        data_transformer = DataTransformer()
        
        # Fetch data
        logging.info("Fetching data from API")
        raw_data = api_client.fetch_data()
        
        if not raw_data:
            logging.warning("No data received from API")
            return
            
        logging.info(f"Received {len(raw_data)} records from API")
        
        # Process data
        logging.info("Cleaning data")
        cleaned_data = data_cleaner.clean(raw_data)
        
        logging.info("Transforming data")
        transformed_data = data_transformer.transform(cleaned_data)
        
        # Store data
        logging.info("Storing processed data in database")
        db_manager.store_data(transformed_data)
        
        # Generate report
        logging.info("Generating report")
        report_gen = ReportGenerator()
        report_path = report_gen.generate_daily_report()
        
        logging.info(f"Report generated successfully: {report_path}")
        
    except Exception as e:
        logging.error(f"Error in data processing job: {str(e)}")
        raise
    
    logging.info(f"Data processing job completed at {datetime.now()}")

def main():
    """Main function to initialize and run the bot"""
    # Setup logging
    setup_logging()
    
    logging.info("Initializing Data Automation Bot")
    
    try:
        # Initialize database
        db = DatabaseManager()
        db.initialize_database()
        
        # Set up scheduler
        scheduler = JobScheduler()
        
        # Register jobs
        scheduler.add_job(
            process_data_job, 
            "data_processing", 
            interval=config.SCHEDULER_INTERVAL,
            retry_attempts=config.RETRY_ATTEMPTS,
            retry_delay=config.RETRY_DELAY
        )
        
        # Start scheduler
        logging.info("Starting scheduler")
        scheduler.start()
        
        # Keep main thread alive
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            logging.info("Received shutdown signal")
            scheduler.stop()
            logging.info("Scheduler stopped")
            
    except Exception as e:
        logging.error(f"Fatal error: {str(e)}")
        return 1
        
    return 0

if __name__ == "__main__":
    sys.exit(main())
