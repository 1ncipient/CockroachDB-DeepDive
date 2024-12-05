import os
import logging
from logging.handlers import RotatingFileHandler
from flask import request
from flask import current_app
import colorlog

# Create logs directory if it doesn't exist
if not os.path.exists('logs'):
    os.makedirs('logs')

def get_logger():
    """Configure and return a logger with colored output."""
    logger = logging.getLogger()
    
    if not logger.handlers:
        # Create console handler with colored formatter
        console_handler = colorlog.StreamHandler()
        
        # Define color scheme
        formatter = colorlog.ColoredFormatter(
            "%(purple)s[%(asctime)s]%(reset)s %(log_color)s%(levelname)-8s%(reset)s %(cyan)s%(module)s%(reset)s: %(message_log_color)s%(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
            reset=True,
            log_colors={
                'DEBUG':    'cyan',
                'INFO':     'green',
                'WARNING': 'yellow',
                'ERROR':   'red',
                'CRITICAL': 'red,bg_white',
            },
            secondary_log_colors={
                'message': {
                    'DEBUG':    'cyan',
                    'INFO':     'white',
                    'WARNING': 'yellow',
                    'ERROR':   'red',
                    'CRITICAL': 'red,bg_white',
                }
            },
            style='%'
        )
        
        # Add formatter to handler
        console_handler.setFormatter(formatter)
        
        # Add handler to logger
        logger.addHandler(console_handler)
        
        # Set logging level
        logger.setLevel(logging.INFO)
    
    return logger

# Configure logging
def setup_logging(app):
    # Set the basic logging level
    app.logger.setLevel(logging.INFO)
    
    # Create formatters and handlers
    formatter = logging.Formatter(
        '[%(asctime)s] %(levelname)s in %(module)s: %(message)s'
    )
    
    # File handler for general logs
    file_handler = RotatingFileHandler(
        'logs/movie_rating_system.log', 
        maxBytes=10485760,  # 10MB
        backupCount=10
    )
    file_handler.setFormatter(formatter)
    file_handler.setLevel(logging.INFO)
    
    # Error file handler
    error_file_handler = RotatingFileHandler(
        'logs/errors.log',
        maxBytes=10485760,  # 10MB
        backupCount=10
    )
    error_file_handler.setFormatter(formatter)
    error_file_handler.setLevel(logging.ERROR)
    
    # Add handlers to the app
    app.logger.addHandler(file_handler)
    app.logger.addHandler(error_file_handler)
    
    # Error logging
    @app.errorhandler(Exception)
    def handle_exception(e):
        app.logger.error(f"Unhandled Exception: {str(e)}", exc_info=True)
        return "Internal Server Error", 500

    return app 