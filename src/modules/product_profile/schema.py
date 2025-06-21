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
    document_name: str = Field(..., description="Title of the product profile document.")
    file_name: str = Field(..., description="File name of the document, including extension.")
    url: str = Field(..., description="Direct link to download or view the document.")
    uploaded_at: str = Field(..., description="Timestamp indicating when the document was uploaded.")
    author: str = Field(..., description="Name of the person or entity that authored the document.")
    size: int = Field(..., description="Document size in bytes.")
