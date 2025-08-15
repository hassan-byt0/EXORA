import aio_pika
import json
from .config import settings
from .logger import get_logger
from .mcp_protocol import MCPMessage

logger = get_logger()

async def send_mcp_message(message: MCPMessage, host: str):
    try:
        # Connect to RabbitMQ
        connection = await aio_pika.connect_robust(
            host=host,
            login=settings.rabbitmq_user,
            password=settings.rabbitmq_password
        )
        
        async with connection:
            channel = await connection.channel()
            
            # Declare exchange
            exchange = await channel.declare_exchange(
                "aahb.mcp",
                aio_pika.ExchangeType.DIRECT,
                durable=True
            )
            
            # Serialize message
            message_body = json.dumps(message.dict()).encode()
            
            # Publish message
            await exchange.publish(
                aio_pika.Message(
                    body=message_body,
                    delivery_mode=aio_pika.DeliveryMode.PERSISTENT
                ),
                routing_key=message.header.destination.lower()
            )
            
            logger.debug(f"MCP message sent to {message.header.destination}")
            
    except Exception as e:
        logger.error(f"Failed to send MCP message: {str(e)}")
        raise