import requests
import os
from dotenv import load_dotenv

load_dotenv()

reservoir_api_key = os.getenv("RESERVOIR_API_KEY")
headers = {"accept": "*/*", "x-api-key": reservoir_api_key}


# Get the top selling nft collections
def get_token_transfers_history(
    contract=None, token=None, collection=None, limit=1, txHash=None, orderBy=None
):
    print(limit, contract)
    url = "https://api.reservoir.tools/transfers/v3"

    if limit is None:
        limit = 5

    parameters = {
        "contract": contract,
        "token": token,
        "collection": collection,
        "txHash": txHash,
        "orderBy": orderBy,
        "limit": limit,
    }
    print(parameters)
    # Construct querystring with only parameters that are not None
    querystring = {k: v for k, v in parameters.items() if v is not None}

    print(querystring)

    # Make the API call
    response = requests.get(url, headers=headers, params=querystring)

    # print(response.text)
    return response.json()
