from typing import Literal
from pydantic import BaseModel


Category = Literal[
    "Technical",
    "Administrative",
    "Legal",
    "Financial",
    "Deadline",
    "Deliverable",
    "Eligibility",
    "Other",
]

RequirementType = Literal[
    "Requirement",
    "EvaluationCriterion",
    "Deadline",
    "Deliverable",
]

#Objeto final de TenderLens
class Requirement(BaseModel):
    id: str | None = None
    tender_id: str
    document_id: str
    category: Category
    sub_category: str | None = None
    requirement_type: RequirementType
    description: str
    mandatory: bool | None
    source_document: str
    pdf_page: int
    page_label: str | None = None
    section: str | None = None
    evidence_text: str

#Resultado final del documento
class ExtractionResult(BaseModel):
    document_id: str
    source_document: str
    requirements: list[Requirement]

#Objeto producido por el LLM
class ExtractedRequirement(BaseModel):
    category: Category
    sub_category: str | None = None
    requirement_type: RequirementType
    description: str
    mandatory: bool | None
    pdf_page: int
    page_label: str | None = None
    section: str | None = None
    evidence_text: str
    
#Lista de objetos producidos por el LLM
class LLMExtractionResult(BaseModel):
    requirements: list[ExtractedRequirement]



