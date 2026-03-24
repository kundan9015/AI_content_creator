"""
Logging system for the application
"""
import logging
import sys
from pathlib import Path
from datetime import datetime
from config.settings import LOGS_DIR, LOG_LEVEL


class Logger:
    def __init__(self, name: str = "ai_content_creator"):
        self.name = name
        self.logger = self._setup_logger()

    def _setup_logger(self):
        """Setup logger with file and console handlers"""
        logger = logging.getLogger(self.name)
        logger.setLevel(getattr(logging, LOG_LEVEL))

        # Remove existing handlers
        logger.handlers = []

        # Format
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )

        # File handler
        log_file = LOGS_DIR / f"app_{datetime.now().strftime('%Y%m%d')}.log"
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_formatter = logging.Formatter(
            '%(levelname)s - %(message)s'
        )
        console_handler.setFormatter(console_formatter)
        logger.addHandler(console_handler)

        return logger

    def info(self, message: str):
        """Log info message"""
        self.logger.info(message)

    def warning(self, message: str):
        """Log warning message"""
        self.logger.warning(message)

    def error(self, message: str):
        """Log error message"""
        self.logger.error(message)

    def debug(self, message: str):
        """Log debug message"""
        self.logger.debug(message)

    def success(self, message: str):
        """Log success message"""
        self.logger.info(f"✓ {message}")

    def separator(self):
        """Log separator line"""
        self.logger.info("=" * 60)


# Global logger instance
logger = Logger()
