from logging import getLogger
from loggers_my.config.logging_config_manager import setup_logging


# Setup custom logging configuration
setup_logging()
# Logger initialize
logger_ukrnet = getLogger("parser_app.management.commands.ukrnet")


