# Geo_processr/sentinel_auth.py
# This is responsible for authenticating the details and ensure it's correct and get token

import os
import requests
from dotenv import load_dotenv
load_dotenv()

def get_sentinel_access_token():
    url = "https://services.sentinel-hub.com/oauth/token"
    payload = {
        "grant_type": "client_credentials",
        "client_id": os.getenv("SENTINEL_CLIENT_ID"),
        "client_secret": os.getenv("SENTINEL_CLIENT_SECRET")
    } # get the details from the env file and send it to the website to get  response

    response = requests.post(url, data=payload) #sending the details
    response.raise_for_status()  # Raise an error if request failed

    access_token = response.json().get("access_token") # Extract the access_token
    return access_token
