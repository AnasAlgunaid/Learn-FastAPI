# logging_config.py
from loguru import logger
import sys

# Configure Loguru to output to stdout and log file with rotation
logger.remove()
logger.add(sys.stdout, format="{time} {level} {message}", level="ERROR")
logger.add(
    "app.log", rotation="500 MB", retention="10 days", format="{time} {level} {message}"
)

# This will make logger available for import in other modules
__all__ = ["logger"]
