from datetime import datetime
from pydantic import BaseModel, Field

from src.modules.product_profile.schema import Feature, Performance


# ============================
# Competitive Analysis Request
# ============================


class UpdateCompetitiveAnalysisRequest(BaseModel):
    product_name: str | None = Field(None, description="Name of the product")
    category: str | None = Field(
        None, description="Category of the competitive analysis"
    )
    regulatory_pathway: str | None = Field(
        None, description="Regulatory pathway for the product"
    )
    clinical_study: str | None = Field(
        None, description="Clinical study information for the product"
    )
    fda_approved: bool | None = Field(
        None, description="Indicates if the product is FDA approved"
    )
    ce_marked: bool | None = Field(
        None, description="Indicates if the product is CE marked"
    )
    is_ai_generated: bool | None = Field(
        None, description="Indicates if the analysis is AI generated"
    )


class UploadTextInputDocumentRequest(BaseModel):
    text: str = Field(..., description="Text input for the document")
    category: str = Field(..., description="Category of the document")


# ============================
# Competitive Analysis Response
# ============================


class CompetitiveAnalysisResponse(BaseModel):
    id: str = Field(..., description="ID of the competitive analysis")
    product_name: str = Field(..., description="Name of the product")
    reference_number: str = Field(
        ..., description="Reference Number of the competitive analysis"
    )
    regulatory_pathway: str = Field(
        ..., description="Regulatory pathway for the product"
    )
    fda_approved: bool = Field(
        ..., description="Indicates if the product is FDA approved"
    )
    ce_marked: bool = Field(..., description="Indicates if the product is CE marked")
    is_ai_generated: bool = Field(
        ..., description="Indicates if the analysis is AI generated"
    )
    confidence_score: float = Field(
        ..., description="Confidence score of the competitive analysis"
    )
    sources: list[str] = Field(
        ..., description="List of sources for the competitive analysis"
    )


class CompetitiveAnalysisDetailResponse(BaseModel): ...


class CompetitiveAnalysisCompareSummary(BaseModel):
    title: str = Field(..., description="Title of the summary")
    summary: str = Field(..., description="Summary of the competitive analysis item")
    icon: str | None = Field(
        None, description="Icon representing the competitive analysis item"
    )


class CompetitiveAnalysisCompareItemResponse(BaseModel):
    product_name: str = Field(..., description="Name of the product")
    price: int = Field(..., description="Price of the product")
    features: list[Feature] = Field(..., description="List of features of the product")
    performance: Performance = Field(
        ..., description="Performance metrics of the product"
    )
    summary: CompetitiveAnalysisCompareSummary = Field(
        ..., description="Summary of the competitive analysis item"
    )


class CompetitiveAnalysisCompareResponse(BaseModel):
    your_product: CompetitiveAnalysisCompareItemResponse = Field(
        ..., description="Details of your product in the competitive analysis"
    )
    competitor: CompetitiveAnalysisCompareItemResponse = Field(
        ..., description="Details of the competitor product in the competitive analysis"
    )


class CompetitiveDeviceAnalysisItemResponse(BaseModel):
    id: str = Field(..., description="ID of the device analysis item")
    content: str = Field(..., description="Content of the device analysis item")
    instructions: list[str] = Field(
        ..., description="List of instructions for the device analysis item"
    )
    type_of_use: str = Field(
        ..., description="Type of use for the device (e.g., diagnostic, therapeutic)"
    )
    fda_approved: bool = Field(
        ..., description="Indicates if the device is FDA approved"
    )
    ce_marked: bool = Field(..., description="Indicates if the device is CE marked")


class CompetitiveDeviceAnalysisKeyDifferenceResponse(BaseModel):
    title: str = Field(..., description="Title of the key difference")
    content: str = Field(
        ..., description="Content describing the key difference between devices"
    )
    icon: str | None = Field(None, description="Icon representing the key difference")


class CompetitiveDeviceAnalysisResponse(BaseModel):
    your_device: CompetitiveDeviceAnalysisItemResponse = Field(
        ..., description="Details of your device in the competitive analysis"
    )
    competitor_device: CompetitiveDeviceAnalysisItemResponse = Field(
        ..., description="Details of the competitor device in the competitive analysis"
    )
    key_differences: list[CompetitiveDeviceAnalysisKeyDifferenceResponse] = Field(
        ..., description="List of key differences between the devices"
    )
    recommendations: list[str] = Field(
        ..., description="List of recommendations based on the competitive analysis"
    )


class CompetitiveAnalysisDocumentResponse(BaseModel):
    document_name: str = Field(
        ..., description="Name of the competitive analysis document"
    )
    file_name: str = Field(..., description="Name of the document")
    url: str = Field(..., description="URL to access the document")
    category: str = Field(..., description="Category of the document")
    uploaded_at: str = Field(
        ..., description="Date and time when the document was uploaded"
    )
    author: str = Field(..., description="Author of the document")
    content_type: str = Field(
        ..., description="Content type of the document (e.g., PDF, DOCX)"
    )
    size: int = Field(..., description="Size of the document in bytes")


class AnalyzeCompetitiveAnalysisProgressResponse(BaseModel):
    reference_product_id: str = Field(..., description="ID of the reference product")
    total_files: int = Field(..., description="Total number of files")
    processed_files: int = Field(
        ..., description="Number of files that have been processed"
    )
    updated_at: datetime = Field(
        ..., description="Date and time when the progress was last updated"
    )
