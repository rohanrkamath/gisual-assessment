'''
security feature 1: api key. This will not let unwanted users get access to the API, and malicious users away. add an
env var/ dotenv file with the key for the code to run.
'''

from fastapi.security.api_key import APIKeyHeader, APIKey
from fastapi import Depends, HTTPException
import os

API_KEY_NAME = "X-API-KEY"
# Define the expected API key (in a real application, store this securely)
API_KEY = os.getenv("API_KEY")
# API_KEY = os.getenv("API_KEY") # kubernetes config

# Create an API key header dependency
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)

def validate_api_key(api_key: str = Depends(api_key_header)) -> str:
    if api_key == API_KEY:
        return api_key
    raise HTTPException(status_code=403, detail="Invalid API Key")