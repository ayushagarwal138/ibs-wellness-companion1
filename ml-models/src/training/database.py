"""
Database connection utilities for ML training pipeline.
"""

import os
import logging
import psycopg2
import pandas as pd
from typing import Optional, Dict, Any
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine

logger = logging.getLogger(__name__)


class DatabaseConnection:
    """Handles database connections for ML training pipeline."""
    
    def __init__(self, database_url: Optional[str] = None):
        """
        Initialize database connection.
        
        Args:
            database_url: PostgreSQL connection URL. If None, uses environment variable.
        """
        self.database_url = database_url or os.getenv(
            'DATABASE_URL', 
            'postgresql://postgres:postgres@localhost:5432/ibs_wellness'
        )
        self.engine: Optional[Engine] = None
        
    def connect(self) -> Engine:
        """
        Create and return SQLAlchemy engine.
        
        Returns:
            SQLAlchemy engine for database operations
        """
        try:
            self.engine = create_engine(self.database_url)
            # Test connection
            with self.engine.connect() as conn:
                conn.execute("SELECT 1")
            logger.info("Successfully connected to database")
            return self.engine
        except Exception as e:
            logger.error(f"Failed to connect to database: {e}")
            raise
    
    def get_connection(self):
        """
        Get database connection for pandas operations.
        
        Returns:
            Database connection object
        """
        if not self.engine:
            self.connect()
        return self.engine
    
    def test_connection(self) -> bool:
        """
        Test if database connection is working.
        
        Returns:
            True if connection successful, False otherwise
        """
        try:
            engine = self.connect()
            with engine.connect() as conn:
                result = conn.execute("SELECT COUNT(*) FROM users")
                count = result.scalar()
                logger.info(f"Database connection test successful. Found {count} users.")
                return True
        except Exception as e:
            logger.error(f"Database connection test failed: {e}")
            return False
    
    def get_table_info(self) -> Dict[str, Any]:
        """
        Get information about available tables and their row counts.
        
        Returns:
            Dictionary with table information
        """
        if not self.engine:
            self.connect()
            
        tables_info = {}
        
        # List of tables we're interested in for ML training
        tables = [
            'users', 'symptoms', 'diet_logs', 'medications', 
            'medication_logs', 'ml_predictions', 'food_items'
        ]
        
        try:
            with self.engine.connect() as conn:
                for table in tables:
                    try:
                        result = conn.execute(f"SELECT COUNT(*) FROM {table}")
                        count = result.scalar()
                        tables_info[table] = {
                            'row_count': count,
                            'available': True
                        }
                        logger.info(f"Table {table}: {count} rows")
                    except Exception as e:
                        tables_info[table] = {
                            'row_count': 0,
                            'available': False,
                            'error': str(e)
                        }
                        logger.warning(f"Could not access table {table}: {e}")
        except Exception as e:
            logger.error(f"Failed to get table information: {e}")
            
        return tables_info
    
    def close(self):
        """Close database connection."""
        if self.engine:
            self.engine.dispose()
            logger.info("Database connection closed")


def get_database_connection(database_url: Optional[str] = None) -> DatabaseConnection:
    """
    Factory function to create database connection.
    
    Args:
        database_url: Optional database URL
        
    Returns:
        DatabaseConnection instance
    """
    return DatabaseConnection(database_url)


def check_database_availability() -> bool:
    """
    Check if database is available and has data.
    
    Returns:
        True if database is available with data, False otherwise
    """
    try:
        db = get_database_connection()
        if not db.test_connection():
            return False
            
        table_info = db.get_table_info()
        
        # Check if we have users and symptoms data (minimum required)
        users_available = table_info.get('users', {}).get('row_count', 0) > 0
        symptoms_available = table_info.get('symptoms', {}).get('row_count', 0) > 0
        
        if users_available and symptoms_available:
            logger.info("Database is available with sufficient data for training")
            return True
        else:
            logger.warning("Database is available but lacks sufficient data for training")
            return False
            
    except Exception as e:
        logger.error(f"Database availability check failed: {e}")
        return False