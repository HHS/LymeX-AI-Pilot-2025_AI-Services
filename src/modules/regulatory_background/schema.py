from pydantic import BaseModel, Field
from typing import List, Optional

# ===== SUMMARY =====
class RegulatorySummaryHighlight(BaseModel):
    title: str
    detail: str

class RegulatorySummary(BaseModel):
    title: str
    description: str
    highlights: List[RegulatorySummaryHighlight]

# ===== FINDINGS =====
class RegulatoryFinding(BaseModel):
    status: str  # "found" or "missing"
    field: str
    label: str
    value: Optional[str]
    sourceFile: Optional[str]
    sourcePage: Optional[int]
    tooltip: Optional[str] = None
    suggestion: Optional[str] = None
    confidenceScore: Optional[int] = None
    userAction: Optional[bool] = None

# ===== CONFLICTS =====
class RegulatoryConflict(BaseModel):
    field: str
    phrase: str
    conflict: str
    source: str
    suggestion: Optional[str] = None
    userAction: Optional[bool] = None

# ===== MAIN SCHEMA =====
class RegulatoryBackgroundSchema(BaseModel):
    summary: RegulatorySummary
    findings: List[RegulatoryFinding]
    conflicts: List[RegulatoryConflict]

# ===== DOCUMENT METADATA =====
class RegulatoryBackgroundDocumentResponse(BaseModel):
    document_name: str = Field(..., description="Name of the regulatory background document")
    file_name: str = Field(..., description="Name of the document")
    url: str = Field(..., description="URL to access the document")
    uploaded_at: str = Field(..., description="Date and time when the document was uploaded")
    author: str = Field(..., description="Author of the document")
    size: int = Field(..., description="Size of the document in bytes")
    key: str = Field(..., description="Key of the document in the storage system")
    path: str = Field(..., description="Path to the document in the local machine")
