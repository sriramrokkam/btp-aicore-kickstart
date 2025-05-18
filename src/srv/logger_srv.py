import logging
import sys

# Configure root logger
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s in %(module)s: %(message)s',
    stream=sys.stdout
)

logger = logging.getLogger("langgraph-btp")


def log_info(message):
    logger.info(message)

def log_error(message):
    logger.error(message)

def log_exception(message, exc: Exception = None):
    if exc:
        logger.error(f"{message} | Exception: {exc}", exc_info=True)
    else:
        logger.error(message, exc_info=True)
