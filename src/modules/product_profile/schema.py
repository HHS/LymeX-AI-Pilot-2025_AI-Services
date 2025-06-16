from datetime import datetime
from pydantic import BaseModel, Field


class RegulatoryClassification(BaseModel):
    organization: str
    classification: str


class Feature(BaseModel):
    name: str
    description: str
    icon: str | None = Field(None, description="Icon representing the feature")


class Performance(BaseModel):
    speed: int
    reliability: int


class ProductProfileDocumentResponse(BaseModel):
    document_name: str = Field(..., description="Name of the product profile document")
    file_name: str = Field(..., description="Name of the document")
    url: str = Field(..., description="URL to access the document")
    uploaded_at: str = Field(
        ..., description="Date and time when the document was uploaded"
    )
    author: str = Field(..., description="Author of the document")
    size: int = Field(..., description="Size of the document in bytes")
