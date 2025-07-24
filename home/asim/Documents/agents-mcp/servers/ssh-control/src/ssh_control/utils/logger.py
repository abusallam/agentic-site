"""
Logging utility for SSH Control MCP Server
"""

import logging
import sys
from datetime import datetime

class Logger:
    """Simple logger for SSH Control MCP Server"""
    
    _logger = None
    
    @classmethod
    def _get_logger(cls):
        """Get or create logger instance"""
        if cls._logger is None:
            cls._logger = logging.getLogger("ssh-control-mcp")
            cls._logger.setLevel(logging.INFO)
            
            # Create console handler
            handler = logging.StreamHandler(sys.stdout)
            handler.setLevel(logging.INFO)
            
            # Create formatter
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            
            # Add handler to logger
            cls._logger.addHandler(handler)
        
        return cls._logger
    
    @classmethod
    def info(cls, message: str):
        """Log info message"""
        cls._get_logger().info(message)
    
    @classmethod
    def warning(cls, message: str):
        """Log warning message"""
        cls._get_logger().warning(message)
    
    @classmethod
    def error(cls, message: str):
        """Log error message"""
        cls._get_logger().error(message)
    
    @classmethod
    def debug(cls, message: str):
        """Log debug message"""
        cls._get_logger().debug(message)