from azure.eventhub import EventHubProducerClient, EventData
import json
import logging
import os
from dotenv import load_dotenv

'''
1. Load env variables
2. defines send_to_eventhub as JSON
3. initialises event hub producer
4. converts dict into json and wraps it in EventData object
5. creats event batch -> adds data -> sends to event hub
6. logs success, errors, etc
'''

load_dotenv()  # optional if using .env file

# Read from environment or config
EVENTHUB_CONN_STR = os.getenv("EVENTHUB_CONNECTION_STRING")
EVENTHUB_NAME = os.getenv("EVENTHUB_NAME")

def send_to_eventhub(data: dict) -> bool:
    """
    Sends a single dictionary as JSON to Azure Event Hub.
    
    Args:
        data (dict): The transaction data to send.
        
    Returns:
        bool: True if successful, False otherwise.
    """
    try:
        # Initialize Event Hub producer
        producer = EventHubProducerClient.from_connection_string(
            conn_str=EVENTHUB_CONN_STR,
            eventhub_name=EVENTHUB_NAME
        )

        # Convert to JSON and wrap in EventData
        event_data = EventData(json.dumps(data))

        # Send the event
        with producer:
            event_batch = producer.create_batch()
            event_batch.add(event_data)
            producer.send_batch(event_batch)

        logging.info(f"Sent event to Event Hub: {data}")
        return True

    except Exception as e:
        logging.error(f"Failed to send to Event Hub: {e}")
        return False
