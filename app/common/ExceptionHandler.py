import logging
import os
import sys
from colorlog import ColoredFormatter
from dotenv import load_dotenv

load_dotenv()

log_file = os.getenv("LOG_FILE")


class DataScienceExceptionHandler:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.setup_logging()

    def setup_logging(self):
        # Define a custom format for log messages with colors
        log_format = "%(log_color)s%(asctime)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s"

        color_formatter = ColoredFormatter(
            log_format,
            datefmt=None,
            reset=True,
            log_colors={
                'DEBUG': 'bold_blue',
                'INFO': 'bold_green',
                'WARNING': 'bold_yellow',
                'ERROR': 'bold_red',
                'CRITICAL': 'bold_purple',
            },
            secondary_log_colors={},
            style='%'
        )
        # Set up logging with the colored formatter
        handler = logging.StreamHandler()
        handler.setFormatter(color_formatter)
        file_handler = logging.FileHandler(filename='app.log')
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s'
        ))
        logging.basicConfig(
            level=logging.DEBUG,
            handlers=[handler, file_handler]
        )

    def handle_exception(self, exc_type, exc_value, exc_traceback):
        # Get the root logger and log the exception with traceback
        logger = logging.getLogger()
        self.logger.error("Uncaught exception", exc_info=(exc_type, exc_value, exc_traceback))


# Set up global exception handler
sys.excepthook = DataScienceExceptionHandler().handle_exception

# Create a global logger
LOGGER = logging.getLogger(__name__)


def main():
    try:

        LOGGER.info("Starting application")
        raise ValueError("Example exception")
    except Exception as e:
        LOGGER.error(e)
        raise


if __name__ == "__main__":
    main()
