"""
Job scheduler for data automation tasks.
Uses APScheduler to manage recurring and one-time job execution.
"""
import logging
from typing import Dict, Any, Callable, Optional, Union
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.triggers.date import DateTrigger
from apscheduler.jobstores.memory import MemoryJobStore
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class JobScheduler:
    """
    Manages scheduling and execution of automated data processing jobs.
    """
    
    def __init__(self):
        """
        Initialize the job scheduler with a background scheduler.
        """
        self.scheduler = BackgroundScheduler(
            jobstores={'default': MemoryJobStore()},
            job_defaults={'coalesce': True, 'max_instances': 1}
        )
        self._running = False
        logger.info("Job scheduler initialized")
    
    def start(self):
        """
        Start the scheduler if not already running.
        """
        if not self._running:
            self.scheduler.start()
            self._running = True
            logger.info("Job scheduler started")
    
    def stop(self):
        """
        Shutdown the scheduler.
        """
        self.shutdown()
    
    def shutdown(self, wait: bool = True):
        """
        Shutdown the scheduler.
        
        Args:
            wait: If True, waits for all running jobs to complete
        """
        if self._running:
            self.scheduler.shutdown(wait=wait)
            self._running = False
            logger.info("Job scheduler shut down")
    
    def add_job(self, job_id: str, func: Callable, **kwargs) -> str:
        """
        Add a job to the scheduler.
        
        Args:
            job_id: Unique identifier for the job
            func: Function to execute
            **kwargs: Additional arguments to pass to the scheduler
            
        Returns:
            Job ID of the scheduled job
        """
        try:
            job = self.scheduler.add_job(func, id=job_id, replace_existing=True, **kwargs)
            logger.info(f"Job '{job_id}' added to scheduler")
            return job.id
        except Exception as e:
            logger.error(f"Failed to add job '{job_id}': {str(e)}")
            raise
    
    def add_cron_job(self, job_id: str, func: Callable, cron_expression: str, **kwargs) -> str:
        """
        Add a job that runs on a cron schedule.
        
        Args:
            job_id: Unique identifier for the job
            func: Function to execute
            cron_expression: Cron expression (e.g. "0 */2 * * *" for every 2 hours)
            **kwargs: Additional keyword arguments to pass to the function
            
        Returns:
            Job ID of the scheduled job
        """
        trigger = CronTrigger.from_crontab(cron_expression)
        return self.add_job(job_id, func, trigger=trigger, kwargs=kwargs)
    
    def add_interval_job(self, job_id: str, func: Callable, 
                         hours: int = 0, minutes: int = 0, seconds: int = 0, **kwargs) -> str:
        """
        Add a job that runs at regular intervals.
        
        Args:
            job_id: Unique identifier for the job
            func: Function to execute
            hours: Hours between executions
            minutes: Minutes between executions
            seconds: Seconds between executions
            **kwargs: Additional keyword arguments to pass to the function
            
        Returns:
            Job ID of the scheduled job
        """
        trigger = IntervalTrigger(hours=hours, minutes=minutes, seconds=seconds)
        return self.add_job(job_id, func, trigger=trigger, kwargs=kwargs)
    
    def add_one_time_job(self, job_id: str, func: Callable, 
                         run_date: Optional[Union[datetime, str]] = None,
                         delay_seconds: Optional[int] = None, **kwargs) -> str:
        """
        Add a job that runs once at a specific time.
        
        Args:
            job_id: Unique identifier for the job
            func: Function to execute
            run_date: Date/time to run the job
            delay_seconds: Alternative to run_date, seconds to delay before execution
            **kwargs: Additional keyword arguments to pass to the function
            
        Returns:
            Job ID of the scheduled job
        """
        if delay_seconds is not None:
            run_date = datetime.now() + timedelta(seconds=delay_seconds)
        
        trigger = DateTrigger(run_date=run_date)
        return self.add_job(job_id, func, trigger=trigger, kwargs=kwargs)
    
    def remove_job(self, job_id: str) -> bool:
        """
        Remove a job from the scheduler.
        
        Args:
            job_id: ID of the job to remove
            
        Returns:
            True if job was removed, False if job wasn't found
        """
        try:
            self.scheduler.remove_job(job_id)
            logger.info(f"Job '{job_id}' removed from scheduler")
            return True
        except Exception as e:
            logger.warning(f"Failed to remove job '{job_id}': {str(e)}")
            return False
    
    def get_jobs(self) -> list:
        """
        Get a list of all scheduled jobs.
        
        Returns:
            List of job objects
        """
        return self.scheduler.get_jobs()
    
    def pause_job(self, job_id: str) -> bool:
        """
        Pause a job temporarily.
        
        Args:
            job_id: ID of the job to pause
            
        Returns:
            True if successful, False otherwise
        """
        try:
            self.scheduler.pause_job(job_id)
            logger.info(f"Job '{job_id}' paused")
            return True
        except Exception as e:
            logger.warning(f"Failed to pause job '{job_id}': {str(e)}")
            return False
    
    def resume_job(self, job_id: str) -> bool:
        """
        Resume a paused job.
        
        Args:
            job_id: ID of the job to resume
            
        Returns:
            True if successful, False otherwise
        """
        try:
            self.scheduler.resume_job(job_id)
            logger.info(f"Job '{job_id}' resumed")
            return True
        except Exception as e:
            logger.warning(f"Failed to resume job '{job_id}': {str(e)}")
            return False
    
    def is_running(self) -> bool:
        """
        Check if the scheduler is running.
        
        Returns:
            True if scheduler is running, False otherwise
        """
        return self._running
