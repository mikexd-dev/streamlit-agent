import requests
import os
from dotenv import load_dotenv

load_dotenv()

SHOPIFY_ACCESS_KEY = os.getenv("SHOPIFY_ACCESS_KEY")
headers = {"accept": "*/*", "x-api-key": SHOPIFY_ACCESS_KEY}


# Get all abandoned checkouts in shopify store
def get_all_abandoned_checkouts(limit=2):
    url = f"https://authentick-1523.myshopify.com/admin/api/2023-07/checkouts.json?limit=2"

    payload = {}
    headers = {"X-Shopify-Access-Token": SHOPIFY_ACCESS_KEY}

    response = requests.request("GET", url, headers=headers, data=payload)

    return response.json()
