import logging
import sys
from logging.handlers import RotatingFileHandler

# Create detailed formatter
detailed_formatter = logging.Formatter(
    '%(asctime)s | %(name)s | %(levelname)s | %(funcName)s:%(lineno)d | %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

# Main log file - everything
main_handler = RotatingFileHandler('logs/overall.log', maxBytes=20*1024*1024, backupCount=5)
main_handler.setFormatter(detailed_formatter)
main_handler.setLevel(logging.DEBUG)

# Error log file
error_handler = RotatingFileHandler('logs/errors.log', maxBytes=10*1024*1024, backupCount=3)
error_handler.setFormatter(detailed_formatter)
error_handler.setLevel(logging.ERROR)

# Console handler
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setFormatter(logging.Formatter('%(levelname)s | %(message)s'))
console_handler.setLevel(logging.INFO)

# Root logger
root_logger = logging.getLogger()
root_logger.setLevel(logging.DEBUG)
root_logger.addHandler(main_handler)
root_logger.addHandler(error_handler)
root_logger.addHandler(console_handler)

# Requests library logger
requests_logger = logging.getLogger('requests')
requests_logger.setLevel(logging.WARNING)

print("Logging configured: logs/overall.log, logs/errors.log")
