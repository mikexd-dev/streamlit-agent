import requests
import os
from dotenv import load_dotenv

load_dotenv()

reservoir_api_key = os.getenv("RESERVOIR_API_KEY")
headers = {"accept": "*/*", "x-api-key": reservoir_api_key}


# This API will return the best price of every token in a collection that is currently on sale. Note: Prices are returned in the native currency of the network.
def get_token_prices_based_on_collection_address(collection):
    url = f"https://api.reservoir.tools/tokens/floor/v1?collection={collection}"

    # Make the API call
    response = requests.get(url, headers=headers)

    # print(response.text)
    return response.json()
