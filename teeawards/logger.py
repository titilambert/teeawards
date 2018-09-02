"""Module defining loggers."""
  
import logging


LOG_LEVELS = ("DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL")

FORMAT = '%(asctime)-15s - %(levelname)-8s - %(name)s - %(message)s'

logging.basicConfig(format=FORMAT)

# pylint: disable=C0103
main_logger = logging.getLogger('TeeAwards')
main_logger.setLevel(logging.DEBUG)
http_logger = main_logger.getChild('http')
