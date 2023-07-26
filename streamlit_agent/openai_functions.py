import openai
import json
import os
from dotenv import load_dotenv
import functions.shopify as shopify
import functions.nft_collections as nft_collections
import functions.tokens as tokens
import functions.transfers as transfers

load_dotenv()

gpt_model = "gpt-3.5-turbo-0613"
# gpt_model = "gpt-4-0613"

shopify_function_descriptions = [
    {
        "name": "get_all_abandoned_checkouts",
        "description": "useful for when you need to answer questions about abandoned checkouts in shopify store. Function also accept an optional argument of limit, which is the number of abandoned checkouts to return.",
        "parameters": {
            "type": "object",
            "properties": {
                "limit": {
                    "type": "integer",
                    "description": "Amount of items returned in response. Default and max limit is 20. defaults to 20",
                },
            },
            "required": ["limit"],
        },
    },
]

nft_function_descriptions = [
    {
        "name": "get_token_prices_based_on_collection_address",
        "description": "Get the best price of every token in a collection that is currently on sale",
        "parameters": {
            "type": "object",
            "properties": {
                "collection": {
                    "type": "string",
                    "description": "Filter to a particular contract address. Example: 0x8d04a8c79ceb0889bdd12acdf3fa9d207ed3ff63",
                },
            },
            "required": ["collection"],
        },
    },
    {
        "name": "get_token_transfers_history",
        "description": "Get recent transfers for a contract or token.",
        "parameters": {
            "type": "object",
            "properties": {
                "contract": {
                    "type": "string",
                    "description": "Filter to a particular contract address. Example: 0x8d04a8c79ceb0889bdd12acdf3fa9d207ed3ff63",
                },
                "limit": {
                    "type": "integer",
                    "description": "Amount of items returned in response. Default and max limit is 20. defaults to 20",
                },
            },
            "required": ["contract"],
        },
    },
    {
        "name": "get_top_selling_nft_collections",
        "description": "Get the top selling and minting collections",
        "parameters": {
            "type": "object",
            "properties": {
                "startTime": {
                    "type": "string",
                    "description": f"Start time in unix timestamp. Must be less than 2 weeks ago. defaults to 24 hours defaults to 1688326557",
                },
                "endTime": {
                    "type": "string",
                    "description": f"End time in unix timestamp. defaults to now",
                },
                "fillType": {
                    "type": "string",
                    "description": f"Fill types to aggregate from (sale, mint, any) defaults to any",
                },
                "limit": {
                    "type": "integer",
                    "description": "Amount of items returned in response. Default and max limit is 20. defaults to 20",
                },
                "includeRecentSales": {
                    "type": "integer",
                    "description": "If true, 8 recent sales will be included in the response defaults to false",
                },
            },
        },
    },
    {
        "name": "get_user_address_stats",
        "description": "Get all the aggregated stats for a user wallet address, grouped by collection",
        "parameters": {
            "type": "object",
            "properties": {
                "user": {
                    "type": "string",
                    "description": "Filter to a particular user. Example: 0x8d04a8c79ceb0889bdd12acdf3fa9d207ed3ff63",
                },
                "limit": {
                    "type": "integer",
                    "description": "Amount of items returned in response. Default and max limit is 20. defaults to 20",
                },
            },
            "required": ["user"],
        },
    },
    {
        "name": "get_supported_nft_marketplaces",
        "description": "Retrieve a list of marketplaces that is list or sells the NFT collection, require the collection address to be known first",
        "parameters": {
            "type": "object",
            "properties": {
                "collection": {
                    "type": "string",
                    "description": "Filter to a particular collection. Example: 0x8d04a8c79ceb0889bdd12acdf3fa9d207ed3ff63",
                },
            },
            "required": ["collection"],
        },
    },
    {
        "name": "get_nft_collections",
        "description": "Get the latest NFT listings on OpenSea",
        "parameters": {
            "type": "object",
            "properties": {
                "id": {
                    "type": "string",
                    "description": "Filter to a particular collection with collection id, Example: 0x8d04a8c79ceb0889bdd12acdf3fa9d207ed3ff63",
                },
                "slug": {
                    "type": "string",
                    "description": "Filter to a particular collection slug. Example: boredapeyachtclub",
                },
                "collectionsSetId": {
                    "type": "string",
                    "description": "Filter to a particular collection set. Example: 8daa732ebe5db23f267e58d52f1c9b1879279bcdf4f78b8fb563390e6946ea65",
                },
                "community": {
                    "type": "string",
                    "description": "Filter to a particular community. Example: artblocks",
                },
                "contract": {
                    "type": "array",
                    "description": "Filter to an array of nft contract addresses",
                },
                "contract": {
                    "type": "string",
                    "description": "Search for collections that match a string. Example: bored",
                },
                "maxFloorAskPrice": {
                    "type": "number",
                    "description": "Search for collections that match a string. Example: bored",
                },
                "maxFloorAskPrice": {
                    "type": "number",
                    "description": "Maximum floor price of the collection",
                },
                "minFloorAskPrice": {
                    "type": "boolean",
                    "description": "If true, top bid will be returned in the response. defaults to false",
                },
                "includeTopBid": {
                    "type": "boolean",
                    "description": "If true, top bid will be returned in the response. defaults to false",
                },
                "includeAttributes": {
                    "type": "boolean",
                    "description": "If true, attributes will be included in the response. Must filter by id or slug to a particular collection.",
                },
                "includeSalesCount": {
                    "type": "boolean",
                    "description": "If true, sales count (1 day, 7 day, 30 day, all time) will be included in the response. Must filter by id or slug to a particular collection.",
                },
                "includeMintStages": {
                    "type": "boolean",
                    "description": "If true, mint data for the collection will be included in the response. defaults to false",
                },
                "normalizeRoyalties": {
                    "type": "boolean",
                    "description": "If true, prices will include missing royalties to be added on-top. defaults to false",
                },
                "useNonFlaggedFloorAsk": {
                    "type": "boolean",
                    "description": "If true, return the non flagged floor ask. Supported only when normalizeRoyalties is false. defaults to false",
                },
                "sortBy": {
                    "type": "string",
                    "description": "Order the items are returned in the response. Options are #DayVolume, createdAt, or floorAskPrice defaults to allTimeVolume",
                },
                "limit": {
                    "type": "integer",
                    "description": "Amount of items returned in response. Default and max limit is 20. defaults to 20",
                },
                "continuation": {
                    "type": "string",
                    "description": "Use continuation token to request next offset of items.",
                },
                "displayCurrency": {
                    "type": "string",
                    "description": "Input any ERC20 address to return result in given currency",
                },
            },
        },
    },
]


def shopify_function_call(ai_response):
    function_call = ai_response["choices"][0]["message"]["function_call"]
    function_name = function_call["name"]
    arguments = function_call["arguments"]
    if function_name == "get_all_abandoned_checkouts":
        limit = eval(arguments).get("limit")
        return shopify.get_all_abandoned_checkouts(limit)
    else:
        return


def nft_function_call(ai_response):
    function_call = ai_response["choices"][0]["message"]["function_call"]
    function_name = function_call["name"]
    arguments = function_call["arguments"]
    if function_name == "get_supported_nft_marketplaces":
        collection = eval(arguments).get("collection")
        return nft_collections.get_supported_nft_marketplaces(collection)
    elif function_name == "get_top_selling_nft_collections":
        arguments = json.loads(arguments)
        startTime = arguments.get("startTime")
        endTime = arguments.get("endTime")
        fillType = arguments.get("fillType")
        limit = arguments.get("limit")
        includeRecentSales = arguments.get("includeRecentSales")
        return nft_collections.get_top_selling_nft_collections(
            startTime, endTime, fillType, limit, includeRecentSales
        )
    elif function_name == "get_user_address_stats":
        user = eval(arguments).get("user")
        limit = eval(arguments).get("limit")
        return nft_collections.get_user_address_stats(user, limit)
    elif function_name == "get_token_prices_based_on_collection_address":
        collection = eval(arguments).get("collection")
        return tokens.get_token_prices_based_on_collection_address(collection)
    elif function_name == "get_token_transfers_history":
        arguments = json.loads(arguments)
        contract = arguments.get("contract")
        token = arguments.get("token")
        collection = arguments.get("collection")
        txHash = arguments.get("txHash")
        limit = arguments.get("limit")
        orderBy = arguments.get("orderBy")
        return transfers.get_token_transfers_history(
            contract, token, collection, limit, txHash, orderBy
        )
    elif function_name == "get_nft_collections":
        # Load the string as a dictionary
        arguments = json.loads(arguments)

        id = arguments.get("id")
        slug = arguments.get("slug")
        limit = arguments.get("limit")
        includeTopBid = arguments.get("includeTopBid")
        collectionsSetId = arguments.get("collectionsSetId")
        community = arguments.get("community")
        contract = arguments.get("contract")
        maxFloorAskPrice = arguments.get("maxFloorAskPrice")
        minFloorAskPrice = arguments.get("minFloorAskPrice")
        includeTopBid = arguments.get("includeTopBid")
        includeAttributes = arguments.get("includeAttributes")
        includeSalesCount = arguments.get("includeSalesCount")
        includeMintStages = arguments.get("includeMintStages")
        normalizeRoyalties = arguments.get("normalizeRoyalties")
        useNonFlaggedFloorAsk = arguments.get("useNonFlaggedFloorAsk")
        sortBy = arguments.get("sortBy")
        limit = arguments.get("limit")
        continuation = arguments.get("continuation")
        displayCurrency = arguments.get("displayCurrency")

        return nft_collections.get_nft_collections(
            id,
            slug,
            collectionsSetId,
            community,
            contract,
            maxFloorAskPrice,
            minFloorAskPrice,
            includeTopBid,
            includeAttributes,
            includeSalesCount,
            includeMintStages,
            normalizeRoyalties,
            useNonFlaggedFloorAsk,
            sortBy,
            limit,
            continuation,
            displayCurrency,
        )

    else:
        return


def shopify_function_calling(query):
    messages = [{"role": "user", "content": query}]

    print("Initial Query", messages)

    response = openai.ChatCompletion.create(
        model=gpt_model,
        messages=messages,
        functions=shopify_function_descriptions,
        function_call="auto",
    )

    print("Initial Response", response)
    count = 1

    while response["choices"][0]["finish_reason"] == "function_call":
        count += 1
        function_response = shopify_function_call(response)
        messages.append(
            {
                "role": "function",
                "name": response["choices"][0]["message"]["function_call"]["name"],
                "content": json.dumps(function_response),
            }
        )

        print(f"Subsequent Query {count}: ", messages)

        response = openai.ChatCompletion.create(
            model=gpt_model,
            messages=messages,
            functions=shopify_function_descriptions,
            function_call="auto",
        )

        print(f"Subsequent Response {count}: ", response)
    else:
        print("Final Response", response)
        return response["choices"][0]["message"]["content"]


def nft_function_calling(query):
    messages = [{"role": "user", "content": query}]

    print("Initial Query", messages)

    response = openai.ChatCompletion.create(
        model=gpt_model,
        messages=messages,
        functions=nft_function_descriptions,
        function_call="auto",
    )

    print("Initial Response", response)
    count = 1

    while response["choices"][0]["finish_reason"] == "function_call":
        count += 1
        function_response = nft_function_call(response)
        messages.append(
            {
                "role": "function",
                "name": response["choices"][0]["message"]["function_call"]["name"],
                "content": json.dumps(function_response),
            }
        )

        print(f"Subsequent Query {count}: ", messages)

        response = openai.ChatCompletion.create(
            model=gpt_model,
            messages=messages,
            functions=nft_function_descriptions,
            function_call="auto",
        )

        print(f"Subsequent Response {count}: ", response)
    else:
        print("Final Response", response)
        return response["choices"][0]["message"]["content"]
