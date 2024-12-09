from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os
from typing import Dict, Optional
from dotenv import load_dotenv
from movieRatingSystem.logging_config import get_logger
# Load environment variables
load_dotenv()

logger = get_logger()

class DatabaseConfig:
    """Database configuration and connection management."""
    
    def __init__(self):
        self.engines = {}
        self.session_factories = {}
        self._load_config()
    
    def _load_config(self):
        """Load database configurations from environment variables."""
        # CockroachDB configuration
        cockroach_config = {
            'url': os.getenv('COCKROACH_DATABASE_URL'),
            'engine_args': {
                'pool_size': int(os.getenv('DB_POOL_SIZE', '5')),
                'max_overflow': int(os.getenv('DB_MAX_OVERFLOW', '10')),
                'pool_timeout': int(os.getenv('DB_POOL_TIMEOUT', '30')),
                'pool_recycle': int(os.getenv('DB_POOL_RECYCLE', '1800')),
                'connect_args': {
                    'application_name': 'movieDB',
                    'options': '--retry_write=true'
                }
            },
        }
        
        # PostgreSQL configuration
        postgres_config = {
            'url': os.getenv('POSTGRES_DATABASE_URL'),
            'engine_args': {
                'pool_size': int(os.getenv('DB_POOL_SIZE', '5')),
                'max_overflow': int(os.getenv('DB_MAX_OVERFLOW', '10')),
                'pool_timeout': int(os.getenv('DB_POOL_TIMEOUT', '30')),
                'pool_recycle': int(os.getenv('DB_POOL_RECYCLE', '1800')),
                'connect_args': {
                    'application_name': 'movieDB'
                }
            }
        }
        
        # MariaDB configuration
        mariadb_config = {
            'url': os.getenv('MARIADB_DATABASE_URL'),
            'engine_args': {
                'pool_size': int(os.getenv('DB_POOL_SIZE', '5')),
                'max_overflow': int(os.getenv('DB_MAX_OVERFLOW', '10')),
                'pool_timeout': int(os.getenv('DB_POOL_TIMEOUT', '30')),
                'pool_recycle': int(os.getenv('DB_POOL_RECYCLE', '1800')),
                'pool_pre_ping': True,  # Verify connections before usage
            }
        }
        
        # Initialize available databases
        self.db_configs = {
            'cockroach': cockroach_config,
            'postgres': postgres_config,
            'mariadb': mariadb_config
        }
    
    def get_engine(self, db_name: str):
        """Get or create SQLAlchemy engine for the specified database."""
        if db_name not in self.engines:
            config = self.db_configs.get(db_name)
            if not config or not config['url']:
                raise ValueError(f"No configuration found for database: {db_name}")
            
            self.engines[db_name] = create_engine(
                config['url'],
                **config['engine_args']
            )
            logger.info(f"Engine created for {db_name}")
            self.session_factories[db_name] = sessionmaker(bind=self.engines[db_name])
        
        return self.engines[db_name]
    
    def get_session_factory(self, db_name: str):
        """Get session factory for the specified database."""
        if db_name not in self.session_factories:
            self.get_engine(db_name)  # This will create both engine and session factory
        return self.session_factories[db_name]
    
    def create_session(self, db_name: str):
        """Create a new session for the specified database."""
        return self.get_session_factory(db_name)()

# Global database configuration instance
db_config = DatabaseConfig() 