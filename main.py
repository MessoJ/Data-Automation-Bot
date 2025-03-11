import sys
import os
import argparse
import signal
import logging
from datetime import datetime

from .config import load_config
from .scheduler.job_scheduler import JobScheduler

def signal_handler(sig, frame):
    """Handle termination signals to gracefully shut down the application."""
    logging.info("Received termination signal. Shutting down...")
    if hasattr(signal_handler, 'scheduler') and signal_handler.scheduler:
        signal_handler.scheduler.stop()
    sys.exit(0)

def setup_signal_handlers(scheduler):
    """Set up signal handlers for graceful termination."""
    signal_handler.scheduler = scheduler
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description='Data Automation Bot')
    
    parser.add_argument(
        '--config', 
        type=str, 
        default='config.json',
        help='Path to configuration file'
    )
    
    parser.add_argument(
        '--job', 
        type=str, 
        help='Run a specific job and exit'
    )
    
    parser.add_argument(
        '--list-jobs', 
        action='store_true',
        help='List available jobs and exit'
    )
    
    parser.add_argument(
        '--log-level', 
        type=str, 
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
        help='Override logging level'
    )
    
    return parser.parse_args()

def run_single_job(scheduler, job_id):
    """Run a single job and exit."""
    logging.info(f"Running single job: {job_id}")
    
    # Check if job exists in configuration
    jobs_config = scheduler.config.get('scheduler', {}).get('jobs', {})
    if job_id not in jobs_config:
        logging.error(f"Job {job_id} not found in configuration")
        return False
    
    job_config = jobs_config[job_id]
    job_type = job_config.get('type')
    
    # Map job type to execution function
    if job_type == 'data_fetch':
        job_func = scheduler._execute_data_fetch
    elif job_type == 'data_process':
        job_func = scheduler._execute_data_process
    elif job_type == 'report_generate':
        job_func = scheduler._execute_report_generate
    else:
        logging.error(f"Unknown job type: {job_type}")
        return False
    
    # Execute the job directly (not through queue)
    try:
        result = job_func(job_id, job_config)
        if result:
            logging.info(f"Job {job_id} completed successfully")
            return True
        else:
            logging.error(f"Job {job_id} failed")
            return False
    except Exception as e:
        logging.error(f"Error executing job {job_id}: {e}")
        logging.exception(e)
        return False

def list_available_jobs(config):
    """Display information about available jobs."""
    jobs_config = config.get('scheduler', {}).get('jobs', {})
    
    if not jobs_config:
        print("No jobs configured.")
        return
    
    print("\nAvailable Jobs:")
    print("-" * 80)
    print(f"{'Job ID':<20} {'Type':<15} {'Schedule':<20} {'Description'}")
    print("-" * 80)
    
    for job_id, job_config in jobs_config.items():
        job_type = job_config.get('type', 'unknown')
        
        schedule_type = job_config.get('schedule', {}).get('type', 'manual')
        schedule_value = job_config.get('schedule', {}).get('value', '')
        schedule_str = f"{schedule_type} {schedule_value}".strip()
        
        description = ""
        if job_type == 'data_fetch':
            source_type = job_config.get('source_type', '')
            destination = job_config.get('destination_table', '')
            description = f"Fetch data from {source_type} to {destination}"
        elif job_type == 'data_process':
            source = job_config.get('source_table', '')
            destination = job_config.get('destination_table', '')
            description = f"Process data from {source} to {destination}"
        elif job_type == 'report_generate':
            report_type = job_config.get('report_type', '')
            recipients = job_config.get('recipients', [])
            description = f"Generate {report_type} report for {len(recipients)} recipients"
        
        print(f"{job_id:<20} {job_type:<15} {schedule_str:<20} {description}")
    
    print("-" * 80)

def main():
    """Main entry point for the application."""
    # Parse command line arguments
    args = parse_arguments()
    
    # Load configuration
    config = load_config(args.config)
    
    # Override log level if specified
    if args.log_level:
        logging.getLogger().setLevel(getattr(logging, args.log_level))
    
    # Print application banner
    app_name = config.get('app_name', 'Data Automation Bot')
    print(f"\n{app_name}")
    print("=" * len(app_name))
    print(f"Version: 1.0.0")
    print(f"Environment: {config.get('environment', 'development')}")
    print(f"Start time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Configuration: {args.config}")
    print("=" * len(app_name))
    
    # List jobs and exit if requested
    if args.list_jobs:
        list_available_jobs(config)
        return
    
    # Initialize the scheduler
    scheduler = JobScheduler(config)
    
    # Set up signal handlers
    setup_signal_handlers(scheduler)
    
    # Run a specific job if requested
    if args.job:
        success = run_single_job(scheduler, args.job)
        sys.exit(0 if success else 1)
    
    # Start the scheduler
    try:
        scheduler.start()
    except KeyboardInterrupt:
        logging.info("Interrupted by user. Shutting down...")
        scheduler.stop()
    except Exception as e:
        logging.error(f"Error in main loop: {e}")
        logging.exception(e)
        scheduler.stop()
        sys.exit(1)

if __name__ == "__main__":
    main()
