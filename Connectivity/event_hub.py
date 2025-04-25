from azure.eventhub import EventHubConsumerClient
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Retrieve Azure Event Hub details from environment variables
eventhub_namespace = os.getenv("EVENTHUB_NAMESPACE")
eventhub_name = os.getenv("EVENTHUB_NAME")
consumer_group = os.getenv("CONSUMER_GROUP")
connection_str = os.getenv("EVENTHUB_CONNECTION_STR")

# Create a client to connect to the Event Hub
def on_event(partition_context, event):
    print(f"Received event from partition: {partition_context.partition_id}, Data: {event.body_as_str()}")

try:
    # Create a consumer client to read from the Event Hub
    client = EventHubConsumerClient.from_connection_string(connection_str, consumer_group)

    # Receiving from all partitions for a short period to check connectivity
    with client:
        client.receive(on_event=on_event, starting_position="@latest")  # Adjust starting position if needed
        print("Successfully connected to Azure Event Hub!")
except Exception as e:
    print(f"Failed to connect to Azure Event Hub: {str(e)}")
