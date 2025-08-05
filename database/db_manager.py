"""
Database Manager for handling all database operations.

This module manages database connections, schema creation/updates,
and data operations for storing and retrieving processed data.
"""

import logging
from typing import Dict, List, Any, Optional
import sqlalchemy as sa
from sqlalchemy.orm import sessionmaker, declarative_base
from contextlib import contextmanager
from datetime import datetime

import config as config
from utils.helpers import handle_exceptions

# Define base model class
Base = declarative_base()

# Define data model
class ProcessedData(Base):
    """Model representing processed data in the database."""
    
    __tablename__ = "processed_data"
    
    id = sa.Column(sa.Integer, primary_key=True)
    source_id = sa.Column(sa.String(100), nullable=False, index=True)
    data_type = sa.Column(sa.String(50), nullable=False)
    value = sa.Column(sa.Float)
    timestamp = sa.Column(sa.DateTime, default=datetime.now)
    data_metadata = sa.Column(sa.JSON)  # Renamed attribute
    processed_at = sa.Column(sa.DateTime, default=datetime.now)
    
    def __repr__(self):
        return f"<ProcessedData(id={self.id}, source_id='{self.source_id}', type='{self.data_type}')>"

# Add more models as needed
class DataSource(Base):
    """Model representing data sources."""
    
    __tablename__ = "data_sources"
    
    id = sa.Column(sa.Integer, primary_key=True)
    name = sa.Column(sa.String(100), nullable=False, unique=True)
    description = sa.Column(sa.Text)
    api_endpoint = sa.Column(sa.String(200))
    is_active = sa.Column(sa.Boolean, default=True)
    created_at = sa.Column(sa.DateTime, default=datetime.now)
    last_updated = sa.Column(sa.DateTime, onupdate=datetime.now)
    
    def __repr__(self):
        return f"<DataSource(id={self.id}, name='{self.name}')>"

class DatabaseManager:
    """Manager for database operations."""
    
    def __init__(self, conn_string: str = None):
        """
        Initialize the database manager.
        
        Args:
            conn_string: Database connection string. Defaults to config value.
        """
        self.conn_string = conn_string or config.DB_CONN_STRING
        self.engine = None
        self.Session = None
        self._initialize_engine()
        
    def _initialize_engine(self):
        """Initialize the SQLAlchemy engine and session factory."""
        logging.info(f"Initializing database with connection string: {self.conn_string}")
        
        # Ensure SQLite connection string format
        if self.conn_string.startswith('sqlite'):
            # Add check_same_thread=False for SQLite to work with Flask
            if '?' not in self.conn_string:
                self.conn_string += '?check_same_thread=False'
            logging.info(f"Using SQLite connection: {self.conn_string}")
        else:
            logging.info(f"Using database connection: {self.conn_string}")
            
        self.engine = sa.create_engine(self.conn_string)
        self.Session = sessionmaker(bind=self.engine)
        
    @contextmanager
    def get_session(self):
        """Get a database session using context manager for automatic cleanup."""
        session = self.Session()
        try:
            yield session
            session.commit()
        except Exception as e:
            session.rollback()
            logging.error(f"Database error: {str(e)}")
            raise
        finally:
            session.close()
    
    @handle_exceptions
    def initialize_database(self):
        """Create database tables if they don't exist."""
        logging.info("Initializing database schema")
        Base.metadata.create_all(self.engine)
        logging.info("Database schema initialized successfully")
    
    @handle_exceptions
    def store_data(self, data_records: List[Dict[str, Any]]):
        """
        Store processed data records in the database.
        
        Args:
            data_records: List of processed data records to store.
        """
        if not data_records:
            logging.warning("No data records to store")
            return
            
        logging.info(f"Storing {len(data_records)} records in database")
        
        # Convert dictionary records to ORM objects
        db_objects = []
        for record in data_records:
            db_obj = ProcessedData(
                source_id=record.get("source_id", "unknown"),
                data_type=record.get("data_type", "unknown"),
                value=record.get("value"),
                timestamp=record.get("timestamp", datetime.now()),
                data_metadata=record.get("metadata", {})
            )
            db_objects.append(db_obj)
        
        # Store in batches to avoid memory issues with large datasets
        batch_size = config.DATA_BATCH_SIZE
        with self.get_session() as session:
            for i in range(0, len(db_objects), batch_size):
                batch = db_objects[i:i + batch_size]
                session.add_all(batch)
                session.flush()
                logging.debug(f"Stored batch of {len(batch)} records")
        
        logging.info(f"Successfully stored {len(data_records)} records in database")
    
    @handle_exceptions
    def get_data(self, data_type: Optional[str] = None, 
                 start_date: Optional[datetime] = None,
                 end_date: Optional[datetime] = None,
                 limit: int = 1000) -> List[Dict[str, Any]]:
        """
        Retrieve data from the database with optional filtering.
        
        Args:
            data_type: Filter by data type.
            start_date: Filter by start date.
            end_date: Filter by end date.
            limit: Maximum number of records to return.
            
        Returns:
            List of data records as dictionaries.
        """
        with self.get_session() as session:
            query = session.query(ProcessedData)
            
            # Apply filters
            if data_type:
                query = query.filter(ProcessedData.data_type == data_type)
            if start_date:
                query = query.filter(ProcessedData.timestamp >= start_date)
            if end_date:
                query = query.filter(ProcessedData.timestamp <= end_date)
                
            # Apply limit and order
            query = query.order_by(ProcessedData.timestamp.desc()).limit(limit)
            
            # Execute query
            results = query.all()
            
            # Convert ORM objects to dictionaries
            data_records = []
            for result in results:
                data_records.append({
                    "id": result.id,
                    "source_id": result.source_id,
                    "data_type": result.data_type,
                    "value": result.value,
                    "timestamp": result.timestamp,
                    "metadata": result.data_metadata,
                    "processed_at": result.processed_at
                })
            
            return data_records
