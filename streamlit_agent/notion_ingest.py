"""This is the logic for ingesting Notion data into LangChain."""
from pathlib import Path
from langchain.text_splitter import CharacterTextSplitter
from langchain.vectorstores import Pinecone
import faiss
from langchain.vectorstores import FAISS
from langchain.embeddings import OpenAIEmbeddings
import pickle
import os
from dotenv import load_dotenv
import pinecone


load_dotenv()
OPENAPI_API_KEY = os.environ.get("OPENAPI_API_KEY")
PINECONE_API_KEY = os.environ.get("PINECONE_API_KEY")
PINECONE_API_ENV = os.environ.get("PINECONE_API_ENV")
PINECONE_INDEX = os.environ.get("PINECONE_INDEX")

# Here we load in the data in the format that Notion exports it in.
ps = list(Path("../authentick_notion_db/").glob("**/*.md"))

data = []
sources = []
for p in ps:
    with open(p) as f:
        data.append(f.read())
    sources.append(p)

# Here we split the documents, as needed, into smaller chunks.
# We do this due to the context limits of the LLMs.
text_splitter = CharacterTextSplitter(chunk_size=1500, separator="\n")
docs = []
metadatas = []
for i, d in enumerate(data):
    splits = text_splitter.split_text(d)
    docs.extend(splits)
    # for document in data:
    #         document.metadata['source'] = file_name
    metadatas.extend([{"source": sources[i]}] * len(splits))


# Here we create a vector store from the documents and save it to disk.
# embeddings = OpenAIEmbeddings()
# pinecone.init(api_key=PINECONE_API_KEY, environment=PINECONE_API_ENV)
# index_name = PINECONE_INDEX
# Pinecone.from_documents(
#     docs, embeddings, index_name=index_name, namespace="authentick-notion"
# )
# print("done")
store = FAISS.from_texts(docs, OpenAIEmbeddings(), metadatas=metadatas)
faiss.write_index(store.index, "docs.index")
store.index = None
with open("faiss_store.pkl", "wb") as f:
    pickle.dump(store, f)
