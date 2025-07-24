from pydantic import BaseModel, Field


class RegulatoryBackgroundContent(BaseModel):
    title: str = Field(..., description="Title of the regulatory background content")
    content: str = Field(..., description="Content of the regulatory background")
    suggestion: str = Field(..., description="Suggestion for the regulatory background")


class RegulatoryBackgroundBase:
    predicate_device_reference: RegulatoryBackgroundContent
    clinical_trial_requirements: RegulatoryBackgroundContent
    risk_classification: RegulatoryBackgroundContent
    regulatory_submission_history: RegulatoryBackgroundContent
    intended_use_statement: RegulatoryBackgroundContent


class RegulatoryBackgroundSchema(BaseModel, RegulatoryBackgroundBase): ...


class RegulatoryBackgroundDocumentResponse(BaseModel):
    document_name: str = Field(
        ..., description="Name of the regulatory background document"
    )
    file_name: str = Field(..., description="Name of the document")
    url: str = Field(..., description="URL to access the document")
    uploaded_at: str = Field(
        ..., description="Date and time when the document was uploaded"
    )
    author: str = Field(..., description="Author of the document")
    size: int = Field(..., description="Size of the document in bytes")
    key: str = Field(..., description="Key of the document in the storage system")
    path: str = Field(..., description="Path to the document in the local machine")
