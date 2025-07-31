from pydantic import BaseModel, Field


class RegulatoryBackgroundHighlight(BaseModel):
    title: str
    detail: str


class RegulatoryBackgroundSummary(BaseModel):
    title: str
    description: str
    highlights: list[RegulatoryBackgroundHighlight]


class RegulatoryBackgroundFinding(BaseModel):
    status: str
    field: str
    label: str
    value: str
    source_file: str | None
    source_page: int | None
    suggestion: str | None
    tooltip: str | None
    confidence_score: int | None
    user_action: bool | None


class RegulatoryBackgroundConflict(BaseModel):
    field: str
    phrase: str
    conflict: str
    source: str
    suggestion: str
    user_action: bool | None = None


class RegulatoryBackgroundBase:
    summary: RegulatoryBackgroundSummary
    findings: list[RegulatoryBackgroundFinding]
    conflicts: list[RegulatoryBackgroundConflict]


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
