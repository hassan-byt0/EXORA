import logging
import sys
import json
from pythonjsonlogger import jsonlogger
from common.config import settings

class CustomJsonFormatter(jsonlogger.JsonFormatter):
    def add_fields(self, log_record, record, message_dict):
        super().add_fields(log_record, record, message_dict)
        log_record['level'] = record.levelname
        log_record['service'] = 'aahb-api-gateway'
        log_record['environment'] = settings.ENV

def setup_logging():
    logger = logging.getLogger("aahb-api-gateway")
    logger.setLevel(logging.INFO)
    
    # Create console handler
    console_handler = logging.StreamHandler(sys.stdout)
    
    # Use JSON formatter in production
    if settings.ENV == "production":
        formatter = CustomJsonFormatter(
            '%(asctime)s %(levelname)s %(message)s %(module)s %(funcName)s'
        )
    else:
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
    
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # Prevent duplicate logs
    logger.propagate = False
    return logger