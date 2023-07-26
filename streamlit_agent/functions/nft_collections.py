import requests
import os
from dotenv import load_dotenv

load_dotenv()

reservoir_api_key = os.getenv("RESERVOIR_API_KEY")
headers = {"accept": "*/*", "x-api-key": reservoir_api_key}


# Get the top selling nft collections
def get_top_selling_nft_collections(
    startTime=None, endTime=None, fillType=None, limit=20, includeRecentSales=None
):
    print(startTime, endTime, fillType, limit, includeRecentSales)
    url = "https://api.reservoir.tools/collections/top-selling/v1"

    parameters = {
        "startTime": startTime,
        "endTime": endTime,
        "fillType": fillType,
        "limit": limit,
    }

    if limit is None:
        limit = 20

    # Construct querystring with only parameters that are not None
    querystring = {k: v for k, v in parameters.items() if v is not None}

    print(querystring, url)
    # Make the API call
    response = requests.get(url, headers=headers, params=querystring)

    # print(response.text)
    return response.json()


# Get all the aggregated stats for a user wallet address, grouped by collection
def get_user_address_stats(user_address, limit=None):
    print("user address:", user_address)
    url = f"https://api.reservoir.tools/users/{user_address}/collections/v3"

    if limit is None:
        limit = 20

    parameters = {"limit": limit}

    # Construct querystring with only parameters that are not None
    querystring = {k: v for k, v in parameters.items() if v is not None}

    # Make the API call
    response = requests.get(url, headers=headers, params=querystring)

    # print(response.text)
    return response.json()["collections"][:10]


# Find out if the collection is supported by the marketplaces
def get_supported_nft_marketplaces(collection_address):
    url = f"https://api.reservoir.tools/collections/{collection_address}/supported-marketplaces/v1"

    response = requests.get(url, headers=headers)

    # print(response.text)
    return response.json()


# Get the latest NFT collections on marketplaces such as OpenSea
def get_nft_collections(
    id=None,
    slug=None,
    collectionsSetId=None,
    community=None,
    contract=None,
    maxFloorAskPrice=None,
    minFloorAskPrice=None,
    includeTopBid=None,
    includeAttributes=None,
    includeSalesCount=None,
    includeMintStages=None,
    normalizeRoyalties=None,
    useNonFlaggedFloorAsk=None,
    sortBy=None,
    limit=None,
    continuation=None,
    displayCurrency=None,
):
    url = "https://api.reservoir.tools/collections/v5"

    if limit is None:
        limit = 20

    # Parameters dictionary
    parameters = {
        "id": id,
        "slug": slug,
        "collectionsSetId": collectionsSetId,
        "community": community,
        "contract": contract,
        "maxFloorAskPrice": maxFloorAskPrice,
        "minFloorAskPrice": minFloorAskPrice,
        "includeTopBid": includeTopBid,
        "includeAttributes": includeAttributes,
        "includeSalesCount": includeSalesCount,
        "includeMintStages": includeMintStages,
        "normalizeRoyalties": normalizeRoyalties,
        "useNonFlaggedFloorAsk": useNonFlaggedFloorAsk,
        "sortBy": sortBy,
        "limit": limit,
        "continuation": continuation,
        "displayCurrency": displayCurrency,
    }

    # Construct querystring with only parameters that are not None
    querystring = {k: v for k, v in parameters.items() if v is not None}

    # Make the API call
    response = requests.get(url, headers=headers, params=querystring)

    # print(response.text)
    return response.json()
