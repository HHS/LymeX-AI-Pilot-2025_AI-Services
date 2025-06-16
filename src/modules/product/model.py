from datetime import datetime
from beanie import Document, PydanticObjectId


class Product(Document):
    name: str
    code: str | None = None
    model: str
    revision: str
    category: str
    intend_use: str
    patient_contact: bool
    company_id: str
    created_by: str
    created_at: datetime
    updated_by: str
    updated_at: datetime
    edit_locked: bool = False

    class Settings:
        name = "product"

    class Config:
        json_encoders = {
            PydanticObjectId: str,
        }
