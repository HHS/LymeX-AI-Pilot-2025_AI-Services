from src.infrastructure.minio import list_objects


def get_system_data_folder() -> str:
    return "system_data"


async def get_system_data_files() -> list[str]:
    system_data_folder = get_system_data_folder()
    system_data = await list_objects(prefix=f"{system_data_folder}/")
    system_data = [document for document in system_data if not document.is_dir]
    file_names = [document.object_name.split("/")[-1] for document in system_data]
    return file_names
