import requests
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Retrieve Azure Function details from environment variables
function_url = os.getenv("AZURE_FUNCTION_URL")

try:
    # Send a request to the Azure Function
    response = requests.get(function_url)
    
    # Check if the response was successful (status code 200)
    if response.status_code == 200:
        print("Successfully connected to Azure Function!")
    else:
        print(f"Failed to connect to Azure Function. Status Code: {response.status_code}")
except requests.exceptions.RequestException as e:
    print(f"Failed to connect to Azure Function: {str(e)}")
