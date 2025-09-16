import mimetypes
from src.infrastructure.minio import generate_get_object_presigned_url
from src.modules.product_profile.schema import ProductProfileDocumentResponse
from minio.datatypes import Object

from src.modules.product_profile.storage import parse_profile_document_info


async def analyze_product_profile_document(
    obj: Object,
) -> ProductProfileDocumentResponse:
    document_name = obj.object_name.split("/")[-1]
    profile_document_info = parse_profile_document_info(document_name.split(".")[0])
    file_name = profile_document_info["file_name"]
    document = ProductProfileDocumentResponse(
        document_name=document_name,
        file_name=file_name,
        url=await generate_get_object_presigned_url(obj.object_name),
        uploaded_at=obj.last_modified.isoformat(),
        author=profile_document_info["author"],
        content_type=obj.content_type
        or mimetypes.guess_type(file_name)[0]
        or "application/octet-stream",
        size=obj.size,
    )
    return document
