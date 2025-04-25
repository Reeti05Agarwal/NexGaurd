from fastapi import FastAPI
from azure.eventhub import EventHubConsumerClient
import json
import joblib
import pandas as pd
from dotenv import load_dotenv
import os

'''
1. Initialises fast api
2. loads pre trained model
3. connects to azure event hub

4. parses json data from the event
5. converts it into dataframe
6. runs ai model to predict if its fraud or not
7. logs the prediction result to console
8. save prediction to azure sql (TO DO)
9. send the alerts/notification (TO DO)
'''
 

app = FastAPI()
model = joblib.load("fraud_model.pkl")  

# Event Hub connection
EVENT_CONNECTION_STR = os.getenv("EVENTHUB_CONNECTION_STRING")
EVENTHUB_NAME = os.getenv("EVENTHUB_NAME")

def on_event(partition_context, event):
    data = json.loads(event.body_as_str())
    df = pd.DataFrame([data])

    prediction = model.predict(df)[0]
    print(f"Transaction {data['transaction_id']} Prediction: {prediction}")

    # TODO: Save to DB, send alert if fraud

    partition_context.update_checkpoint(event)

@app.on_event("startup")
async def startup_event():
    client = EventHubConsumerClient.from_connection_string(
        EVENT_CONNECTION_STR, consumer_group="$Default", eventhub_name=EVENTHUB_NAME
    )
    client.receive(on_event=on_event, starting_position="-1")

@app.get("/")
def health():
    return {"status": "running"}
