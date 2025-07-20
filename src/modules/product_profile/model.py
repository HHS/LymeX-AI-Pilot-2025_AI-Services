from datetime import datetime
from beanie import Document, PydanticObjectId
from src.modules.product_profile.schema import (
    ProductProfileSchemaBase,
)


class ProductProfile(Document, ProductProfileSchemaBase):
    product_id: str

    class Settings:
        name = "product_profile"

    class Config:
        json_encoders = {
            PydanticObjectId: str,
        }


class AnalyzeProductProfileProgress(Document):
    product_id: str
    total_files: int
    processed_files: int
    updated_at: datetime

    class Settings:
        name = "analyze_product_profile_progress"

    class Config:
        json_encoders = {
            PydanticObjectId: str,
        }
