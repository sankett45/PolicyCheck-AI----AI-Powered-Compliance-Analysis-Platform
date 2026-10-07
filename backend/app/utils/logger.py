import logging
import sys

# Define a standard, readable logging format
LOG_FORMAT = "%(asctime)s [%(levelname)s] %(name)s (%(filename)s:%(lineno)d) - %(message)s"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

# Configure the basic logging setup
logging.basicConfig(
    level=logging.INFO,
    format=LOG_FORMAT,
    datefmt=DATE_FORMAT,
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

# Expose the central logger instance
logger = logging.getLogger("AuditFlow")
logger.setLevel(logging.INFO)