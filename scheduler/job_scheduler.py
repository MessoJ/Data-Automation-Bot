import schedule
import time
import logging
import threading
import queue
from datetime import datetime, timedelta
import traceback

from ..api.api_client import APIClient
from ..database.db_manager import DatabaseManager
from ..data_preprocessing.cleaner import DataCleaner
from ..data_preprocessing.transformer import DataTransformer
from ..reporting.report_generator import ReportGenerator

class JobScheduler:
    def __init__(self, config):
        """
        Initialize the job scheduler with configuration settings.
        
        Parameters:
        -----------
        config : dict
            Configuration dictionary with scheduler settings
        """
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.job_queue = queue.Queue()
        self.is_running = False
        self.worker_threads = []
        self.num_workers = config.get('scheduler', {}).get('num_workers', 1)
        
        # Initialize components
        self.api_client = APIClient(config.get('api', {}))
        self.db_manager = DatabaseManager(config.get('database', {}))
        self.data_cleaner = DataCleaner(config.get('data_preprocessing', {}))
        self.data_transformer = DataTransformer(config.get('data_preprocessing', {}))
        self.report_generator = ReportGenerator(config.get('reporting', {}))
        
        # Job history tracking
        self.job_history = {}
        
    def start(self):
        """
        Start the scheduler and worker threads.
        """
        if self.is_running:
            self.logger.warning("Scheduler is already running")
            return
            
        self.logger.info("Starting scheduler")
        self.is_running = True
        
        # Start worker threads
        for i in range(self.num_workers):
            thread = threading.Thread(
                target=self._worker_thread,
                name=f"Worker-{i+1}",
                daemon=True
            )
            thread.start()
            self.worker_threads.append(thread)
        
        # Schedule jobs based on configuration
        self._schedule_jobs()
        
        # Run the scheduler in the main thread
        while self.is_running:
            schedule.run_pending()
            time.sleep(1)
    
    def stop(self):
        """
        Stop the scheduler and worker threads.
        """
        self.logger.info("Stopping scheduler")
        self.is_running = False
        
        # Add termination tasks to signal workers to stop
        for _ in range(self.num_workers):
            self.job_queue.put(None)
        
        # Wait for all worker threads to finish
        for thread in self.worker_threads:
            thread.join(timeout=5)
        
        self.worker_threads = []
        
    def _worker_thread(self):
        """
        Worker thread that executes jobs from the queue.
        """
        thread_name = threading.current_thread().name
        self.logger.info(f"Starting worker thread: {thread_name}")
        
        while self.is_running:
            try:
                # Get job from queue with timeout to check is_running periodically
                job = self.job_queue.get(timeout=1)
                
                # None is our signal to exit
                if job is None:
                    self.logger.info(f"Worker thread {thread_name} received exit signal")
                    break
                    
                # Execute the job
                job_id, job_func, job_args, job_kwargs = job
                self.logger.info(f"Executing job {job_id}")
                
                start_time = time.time()
                try:
                    result = job_func(*job_args, **job_kwargs)
                    success = True
                    error_message = None
                except Exception as e:
                    result = None
                    success = False
                    error_message = str(e)
                    self.logger.error(f"Error executing job {job_id}: {e}")
                    self.logger.error(traceback.format_exc())
                
                end_time = time.time()
                duration = end_time - start_time
                
                # Update job history
                self._update_job_history(job_id, success, duration, error_message)
                
                # Mark the job as done in the queue
                self.job_queue.task_done()
                
            except queue.Empty:
                # Queue timeout, just continue the loop
                continue
            except Exception as e:
                self.logger.error(f"Worker thread {thread_name} encountered error: {e}")
                self.logger.error(traceback.format_exc())
                
        self.logger.info(f"Worker thread {thread_name} stopped")
    
    def _schedule_jobs(self):
        """
        Schedule jobs based on configuration.
        """
        jobs_config = self.config.get('scheduler', {}).get('jobs', {})
        
        for job_id, job_config in jobs_config.items():
            job_type = job_config.get('type')
            schedule_type = job_config.get('schedule', {}).get('type')
            schedule_value = job_config.get('schedule', {}).get('value')
            
            # Schedule the job based on its type
            if job_type == 'data_fetch':
                job_func = self._execute_data_fetch
                job_args = (job_id, job_config)
            elif job_type == 'data_process':
                job_func = self._execute_data_process
                job_args = (job_id, job_config)
            elif job_type == 'report_generate':
                job_func = self._execute_report_generate
                job_args = (job_id, job_config)
            else:
                self.logger.warning(f"Unknown job type: {job_type} for job {job_id}")
                continue
            
            # Apply the schedule
            if schedule_type == 'interval':
                # Schedule at specific intervals (minutes)
                interval_minutes = int(schedule_value)
                schedule.every(interval_minutes).minutes.do(
                    self._enqueue_job, job_id, job_func, job_args
                )
                self.logger.info(f"Scheduled {job_id} to run every {interval_minutes} minutes")
                
            elif schedule_type == 'daily':
                # Schedule at specific time each day
                schedule.every().day.at(schedule_value).do(
                    self._enqueue_job, job_id, job_func, job_args
                )
                self.logger.info(f"Scheduled {job_id} to run daily at {schedule_value}")
                
            elif schedule_type == 'weekly':
                # Schedule on specific day of week
                day, time_str = schedule_value.split(' ')
                schedule_obj = schedule.every()
                
                if day.lower() == 'monday':
                    schedule_obj = schedule_obj.monday
                elif day.lower() == 'tuesday':
                    schedule_obj = schedule_obj.tuesday
                elif day.lower() == 'wednesday':
                    schedule_obj = schedule_obj.wednesday
                elif day.lower() == 'thursday':
                    schedule_obj = schedule_obj.thursday
                elif day.lower() == 'friday':
                    schedule_obj = schedule_obj.friday
                elif day.lower() == 'saturday':
                    schedule_obj = schedule_obj.saturday
                elif day.lower() == 'sunday':
                    schedule_obj = schedule_obj.sunday
                
                schedule_obj.at(time_str).do(
                    self._enqueue_job, job_id, job_func, job_args
                )
                self.logger.info(f"Scheduled {job_id} to run {day} at {time_str}")
                
            elif schedule_type == 'immediate':
                # Run immediately once
                self._enqueue_job(job_id, job_func, job_args)
                self.logger.info(f"Queued {job_id} to run immediately")
                
            else:
                self.logger.warning(f"Unknown schedule type: {schedule_type} for job {job_id}")
    
    def _enqueue_job(self, job_id, job_func, job_args=(), job_kwargs=None):
        """
        Add a job to the queue for execution.
        
        Parameters:
        -----------
        job_id : str
            Unique identifier for the job
        job_func : callable
            Function to execute
        job_args : tuple, optional
            Arguments to pass to the function
        job_kwargs : dict, optional
            Keyword arguments to pass to the function
            
        Returns:
        --------
        bool
            True to keep the job scheduled, False to unschedule it
        """
        if job_kwargs is None:
            job_kwargs = {}
            
        # Add to the queue
        self.job_queue.put((job_id, job_func, job_args, job_kwargs))
        self.logger.info(f"Job {job_id} added to queue")
        
        # Update job history to show it's been queued
        self._update_job_history(job_id, None, None, None, status='queued')
        
        # Return True to keep the job in the schedule
        return True
    
    def _update_job_history(self, job_id, success=None, duration=None, 
                            error=None, status='completed'):
        """
        Update the job history with execution results.
        
        Parameters:
        -----------
        job_id : str
            Unique identifier for the job
        success : bool, optional
            Whether the job completed successfully
        duration : float, optional
            Duration of the job execution in seconds
        error : str, optional
            Error message if the job failed
        status : str, optional
            Current status of the job (queued, running, completed)
        """
        now = datetime.now()
        
        if job_id not in self.job_history:
            self.job_history[job_id] = []
            
        # Add new execution record
        execution_record = {
            'timestamp': now,
            'status': status
        }
        
        if success is not None:
            execution_record['success'] = success
            
        if duration is not None:
            execution_record['duration'] = duration
            
        if error is not None:
            execution_record['error'] = error
            
        self.job_history[job_id].append(execution_record)
        
        # Limit history size
        max_history = self.config.get('scheduler', {}).get('max_history', 100)
        if len(self.job_history[job_id]) > max_history:
            self.job_history[job_id] = self.job_history[job_id][-max_history:]
    
    def _execute_data_fetch(self, job_id, job_config):
        """
        Execute a data fetch job.
        
        Parameters:
        -----------
        job_id : str
            Unique identifier for the job
        job_config : dict
            Configuration for the job
            
        Returns:
        --------
        bool
            Success status
        """
        self.logger.info(f"Executing data fetch job: {job_id}")
        
        # Extract job-specific configuration
        source_type = job_config.get('source_type')
        source_config = job_config.get('source_config', {})
        
        # Update job status
        self._update_job_history(job_id, None, None, None, status='running')
        
        # Fetch data based on source type
        try:
            if source_type == 'api':
                # Fetch from API
                endpoint = source_config.get('endpoint')
                method = source_config.get('method', 'GET')
                params = source_config.get('params', {})
                
                response = self.api_client.make_request(
                    endpoint=endpoint,
                    method=method,
                    params=params
                )
                
                # Store the raw data
                table_name = job_config.get('destination_table')
                raw_data = response.get('data', [])
                
                self.db_manager.insert_many(
                    table_name=table_name,
                    data=raw_data
                )
                
                self.logger.info(f"Fetched and stored {len(raw_data)} records from API")
                return True
                
            elif source_type == 'database':
                # Fetch from another database
                query = source_config.get('query')
                conn_string = source_config.get('connection_string')
                
                # This would use a different connection than our main one
                # For simplicity, we're using the same db_manager
                result = self.db_manager.execute_query(query)
                
                # Store the results
                table_name = job_config.get('destination_table')
                self.db_manager.df_to_table(result, table_name)
                
                self.logger.info(f"Fetched and stored {len(result)} records from database")
                return True
                
            else:
                self.logger.error(f"Unknown source type: {source_type}")
                return False
                
        except Exception as e:
            self.logger.error(f"Error in data fetch job {job_id}: {e}")
            self.logger.error(traceback.format_exc())
            return False
    
    def _execute_data_process(self, job_id, job_config):
        """
        Execute a data processing job.
        
        Parameters:
        -----------
        job_id : str
            Unique identifier for the job
        job_config : dict
            Configuration for the job
            
        Returns:
        --------
        bool
            Success status
        """
        self.logger.info(f"Executing data processing job: {job_id}")
        
        # Extract job-specific configuration
        source_table = job_config.get('source_table')
        destination_table = job_config.get('destination_table')
        operations = job_config.get('operations', [])
        
        # Update job status
        self._update_job_history(job_id, None, None, None, status='running')
        
        try:
            # Get the data
            query = f"SELECT * FROM {source_table}"
            data = self.db_manager.execute_query(query)
            
            if data.empty:
                self.logger.warning(f"No data found in {source_table}")
                return False
            
            # Apply operations
            processed_data = data.copy()
            
            for operation in operations:
                op_type = operation.get('type')
                op_config = operation.get('config', {})
                
                if op_type == 'clean':
                    processed_data = self.data_cleaner.clean_data(
                        processed_data, **op_config
                    )
                elif op_type == 'transform':
                    processed_data = self.data_transformer.transform_data(
                        processed_data, **op_config
                    )
                else:
                    self.logger.warning(f"Unknown operation type: {op_type}")
            
            # Store the processed data
            self.db_manager.df_to_table(processed_data, destination_table)
            
            self.logger.info(
                f"Processed {len(data)} records from {source_table} "
                f"to {len(processed_data)} records in {destination_table}"
            )
            return True
            
        except Exception as e:
            self.logger.error(f"Error in data processing job {job_id}: {e}")
            self.logger.error(traceback.format_exc())
            return False
    
    def _execute_report_generate(self, job_id, job_config):
        """
        Execute a report generation job.
        
        Parameters:
        -----------
        job_id : str
            Unique identifier for the job
        job_config : dict
            Configuration for the job
            
        Returns:
        --------
        bool
            Success status
        """
        self.logger.info(f"Executing report generation job: {job_id}")
        
        # Extract job-specific configuration
        report_type = job_config.get('report_type')
        report_config = job_config.get('report_config', {})
        recipients = job_config.get('recipients', [])
        
        # Update job status
        self._update_job_history(job_id, None, None, None, status='running')
        
        try:
            report_path = None
            
            if report_type == 'daily':
                # Generate daily report
                report_date = datetime.now().date()
                report_path = self.report_generator.generate_daily_report(report_date)
                
            elif report_type == 'weekly':
                # Generate weekly report
                end_date = datetime.now().date()
                start_date = end_date - timedelta(days=7)
                report_path = self.report_generator.generate_weekly_report(
                    start_date, end_date
                )
                
            elif report_type == 'custom':
                # Generate custom report
                report_path = self.report_generator.generate_custom_report(
                    **report_config
                )
                
            else:
                self.logger.error(f"Unknown report type: {report_type}")
                return False
            
            # Send the report if recipients are specified
            if report_path and recipients:
                self.report_generator.email_report(report_path, recipients)
                
            self.logger.info(f"Generated report: {report_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error in report generation job {job_id}: {e}")
            self.logger.error(traceback.format_exc())
            return False
