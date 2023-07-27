from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import Pinecone

import pinecone
import os
import asyncio
from dotenv import load_dotenv
from process_markdown import process_markdown_files

load_dotenv()
OPENAPI_API_KEY = os.environ.get("OPENAPI_API_KEY")
PINECONE_API_KEY = os.environ.get("PINECONE_API_KEY")
PINECONE_API_ENV = os.environ.get("PINECONE_API_ENV")
PINECONE_INDEX = os.environ.get("PINECONE_INDEX")
PINECONE_NAMESPACE = "authentick-notion"
directory_path = "../../authentick_notion_db"


async def run():
    raw_docs = await process_markdown_files(directory_path)

    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    docs = splitter.split_documents(raw_docs)

    print("Split docs:", docs)

    embeddings = OpenAIEmbeddings()
    pinecone.init(api_key=PINECONE_API_KEY, environment=PINECONE_API_ENV)
    Pinecone.from_documents(
        docs, embeddings, index_name=PINECONE_INDEX, namespace=PINECONE_NAMESPACE
    )

    pinecone.init(api_key=PINECONE_API_KEY, environment=PINECONE_API_ENV)
    index_name = PINECONE_INDEX
    vs = Pinecone.from_documents(
        docs, embeddings, index_name=index_name, namespace="langchain-python"
    )
    # index = VectorstoreIndexCreator(
    #     vectorstore_kwargs={"persist_directory": "./vectors"}
    # ).from_loaders([loader])
    return vs


if __name__ == "__main__":
    asyncio.run(run())

    print("Ingestion complete!")
