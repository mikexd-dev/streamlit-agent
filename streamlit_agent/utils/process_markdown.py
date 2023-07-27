import glob
import asyncio
from langchain.document_loaders.base import Document


async def process_markdown_files(directory_path):
    try:
        file_names = glob.glob(f"{directory_path}/**.md")
        print("files", file_names)

        docs = []
        for file_name in file_names:
            text = await asyncio.to_thread(open(file_name).read)
            metadata = {"source": file_name}
            doc = Document(page_content=text, metadata=metadata)
            docs.append(doc)

        print("docs", docs)
        return docs

    except Exception as e:
        print("error", e)
        raise Exception(f"Could not read directory path {directory_path}")
