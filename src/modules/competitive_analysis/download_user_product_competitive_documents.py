from pathlib import Path

from pydantic import BaseModel
from src.modules.competitive_analysis.storage import get_competitive_analysis_documents
import httpx


class UserProductCompetitiveDocument(BaseModel):
    product_name: str
    user_product_competitive_documents: list[Path]


async def download_user_product_competitive_documents(
    product_id: str,
) -> list[UserProductCompetitiveDocument]:
    competitive_analysis_documents = await get_competitive_analysis_documents(
        product_id
    )
    competitive_analysis_document_paths_dict: dict[str, list[Path]] = {}
    for competitive_analysis_document in competitive_analysis_documents:
        competitive_analysis_document_path = Path(
            f"/tmp/user_competitor_documents/{competitive_analysis_document.file_name}"
        )
        async with httpx.AsyncClient() as client:
            response = await client.get(competitive_analysis_document.url)
            competitive_analysis_document_path.parent.mkdir(parents=True, exist_ok=True)
            with open(competitive_analysis_document_path, "wb") as f:
                f.write(response.content)
        if (
            competitive_analysis_document.category
            not in competitive_analysis_document_paths_dict
        ):
            competitive_analysis_document_paths_dict[
                competitive_analysis_document.category
            ] = []
        competitive_analysis_document_paths_dict[
            competitive_analysis_document.category
        ].append(competitive_analysis_document_path)
    return [
        UserProductCompetitiveDocument(
            product_name=category, user_product_competitive_documents=paths
        )
        for category, paths in competitive_analysis_document_paths_dict.items()
    ]
