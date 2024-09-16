import logging
import os
from dotenv import load_dotenv
load_dotenv()

class Logger:
    """Logger class"""
    def __init__(self) -> None:
        # Configure logging
        self.log_level = os.getenv('LOG_LEVEL', 'ERROR').upper()
        self.log_format = os.getenv("LOG_FORMAT")
        self.logger = None

    def get_logger(self, logger_name:str)->logging.Logger:
        """Returns application logger"""
        logging.getLogger(name='py4j').setLevel(logging.WARNING)
        logging.getLogger(name='urllib3').setLevel(logging.WARNING)
        logging.getLogger(name='azure').setLevel(logging.WARNING)
        # logging.getLogger(name='sentence_transformers').setLevel(logging.WARNING)
        logging.basicConfig(level=self.log_level,format=self.log_format)
        self.logger = logging.getLogger(logger_name)
        return self.logger
