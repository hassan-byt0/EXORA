# tests/conftest.py
import pytest
from dotenv import load_dotenv
from common.config import settings
from common.logger import get_logger

logger = get_logger("tests")

# Load test environment variables
load_dotenv(".env.test")

@pytest.fixture(scope="session")
def test_config():
    """Override configuration for tests"""
    settings.ENV = "testing"
    settings.TEST_MODE = True
    return settings

@pytest.fixture(scope="module")
def neo4j_driver(test_config):
    """Fixture for Neo4j driver"""
    from neo4j import GraphDatabase
    driver = GraphDatabase.driver(
        test_config.NEO4J_URI,
        auth=(test_config.NEO4J_USER, test_config.NEO4J_PASSWORD)
    )
    yield driver
    driver.close()

@pytest.fixture(scope="module")
def rabbitmq_connection(test_config):
    """Fixture for RabbitMQ connection"""
    import pika
    credentials = pika.PlainCredentials(
        test_config.RABBITMQ_USER, 
        test_config.RABBITMQ_PASSWORD
    )
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(
            host=test_config.RABBITMQ_HOST,
            credentials=credentials
        )
    )
    yield connection
    connection.close()

@pytest.fixture(scope="function")
def clean_database(neo4j_driver):
    """Clean database before each test"""
    with neo4j_driver.session() as session:
        session.run("MATCH (n) DETACH DELETE n")
    yield