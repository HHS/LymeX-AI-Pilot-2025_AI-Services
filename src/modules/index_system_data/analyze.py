from pathlib import Path

from src.infrastructure.minio import get_object
from src.infrastructure.qdrant import add_document, delete_document, get_all_documents
from src.modules.index_system_data.storage import (
    get_system_data_files,
    get_system_data_folder,
)
from src.modules.index_system_data.summarize_files import summarize_files


async def index_system_data() -> None:
    system_data_files = await get_system_data_files()
    indexed_system_data = get_all_documents()
    indexed_system_data_filenames = [
        doc["filename"] for doc in indexed_system_data if doc["filename"]
    ]
    print(f"Indexed System Data: {indexed_system_data}")
    print(f"System Data Files: {system_data_files}")
    files_to_index = [
        file for file in system_data_files if file not in indexed_system_data_filenames
    ]
    files_to_unindex = [
        file for file in indexed_system_data_filenames if file not in system_data_files
    ]
    print(f"Files to Index: {files_to_index}")
    print(f"Files to Unindex: {files_to_unindex}")
    system_data_folder = get_system_data_folder()
    for file in files_to_index:
        key = f"{system_data_folder}/{file}"
        print(f"Indexing file: {key}")
        raw_data = await get_object(key)
        # save to temporary file
        temp_path = Path(f"/tmp/{system_data_folder}/{file}")
        temp_path.parent.mkdir(parents=True, exist_ok=True)
        with open(temp_path, "wb") as f:
            f.write(raw_data)
        summary = await summarize_files([temp_path])
        print(f"Summary for {file}: {summary}")

        print(f"• Summarized {file}: {summary!r}")
        add_document(file, summary)

    # 4) remove deleted files from Qdrant
    for filename in files_to_unindex:
        delete_document(filename)
        print(f"  • removed {filename}")
