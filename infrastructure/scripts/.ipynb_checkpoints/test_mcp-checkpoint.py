import pika
import json
import time
from common.mcp_protocol import MCPHeader, MCPMessage
from common.config import settings
from common.logger import get_logger

logger = get_logger("mcp_tester")

def send_test_message():
    # Create MCP message
    header = MCPHeader(
        source="TESTER",
        destination="VISION_AGENT",
        context_id="test-123"
    )
    message = MCPMessage(
        header=header,
        payload={"test_data": "This is a test message"}
    )
    
    # Connect to RabbitMQ
    credentials = pika.PlainCredentials(
        settings.rabbitmq_user, 
        settings.rabbitmq_password
    )
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(
            host=settings.rabbitmq_host,
            credentials=credentials
        )
    )
    channel = connection.channel()
    
    # Declare exchange
    channel.exchange_declare(
        exchange="aahb.mcp",
        exchange_type="direct",
        durable=True
    )
    
    # Publish message
    channel.basic_publish(
        exchange="aahb.mcp",
        routing_key="VISION_AGENT",
        body=message.json().encode(),
        properties=pika.BasicProperties(
            delivery_mode=2  # Make message persistent
        )
    )
    
    logger.info("Test message sent to VISION_AGENT")
    connection.close()

def receive_responses():
    # Connect to RabbitMQ
    credentials = pika.PlainCredentials(
        settings.rabbitmq_user, 
        settings.rabbitmq_password
    )
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(
            host=settings.rabbitmq_host,
            credentials=credentials
        )
    )
    channel = connection.channel()
    
    # Create temporary queue
    result = channel.queue_declare(queue='', exclusive=True)
    queue_name = result.method.queue
    
    # Bind to responses
    channel.queue_bind(
        exchange="aahb.mcp",
        queue=queue_name,
        routing_key="TESTER"
    )
    
    logger.info("Waiting for responses...")
    
    def callback(ch, method, properties, body):
        try:
            message = MCPMessage.parse_raw(body)
            logger.info(f"Received response: {message.payload}")
            ch.basic_ack(delivery_tag=method.delivery_tag)
        except Exception as e:
            logger.error(f"Error processing message: {str(e)}")
    
    channel.basic_consume(
        queue=queue_name,
        on_message_callback=callback
    )
    
    channel.start_consuming()

if __name__ == "__main__":
    send_test_message()
    time.sleep(2)
    receive_responses()