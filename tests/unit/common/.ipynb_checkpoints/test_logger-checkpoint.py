# tests/unit/common/test_logger.py
import pytest
import logging
from common.logger import get_logger, setup_logging
from common.config import settings

def test_logger_setup():
    # Test development logger
    settings.ENV = "development"
    logger = setup_logging()
    assert len(logger.handlers) == 1
    assert isinstance(logger.handlers[0], logging.StreamHandler)
    
    # Test production logger
    settings.ENV = "production"
    logger = setup_logging()
    assert len(logger.handlers) == 1
    assert isinstance(logger.handlers[0].formatter, logging.Formatter)

def test_get_logger():
    logger = get_logger("test_logger")
    assert logger.name == "test_logger"
    assert logger.level == logging.INFO