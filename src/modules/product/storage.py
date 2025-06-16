from src.infrastructure.minio import (
    generate_get_object_presigned_url,
    generate_put_object_presigned_url,
)


async def get_product_avatar_url(product_id: str) -> str:
    avatar_object_name = f"{get_product_folder(product_id)}/avatar"
    avatar_url = await generate_get_object_presigned_url(avatar_object_name)
    return avatar_url


async def get_update_product_avatar_url(product_id: str) -> str:
    avatar_object_name = f"{get_product_folder(product_id)}/avatar"
    avatar_url = await generate_put_object_presigned_url(avatar_object_name)
    return avatar_url


# ================ FOLDERS ====================


def get_product_folder(product_id: str) -> str:
    return f"product/{product_id}"
