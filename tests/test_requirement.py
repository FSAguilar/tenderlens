import pytest
from pydantic import ValidationError

# from src.models.requirement import Requirement
from src.models.requirement import (
    Requirement,
    ExtractionResult,
    ExtractedRequirement,
    LLMExtractionResult,
)

def test_valid_requirement():
    requirement = Requirement(
        id="REQ-001",
        tender_id="snoqualmie_erp",
        document_id="rfp_erp",
        category="Technical",
        sub_category="Architecture",
        requirement_type="Requirement",
        description="The solution must support a Microsoft-centric architecture.",
        mandatory=True,
        source_document="RFP-for-ERP-Software-and-Implementation-Services.pdf",
        pdf_page=2,
        page_label="3",
        section="Technical Requirements",
        evidence_text="Microsoft-centric architecture",
    )

    

    assert requirement.category == "Technical"
    assert requirement.mandatory is True
    assert requirement.pdf_page == 2


def test_invalid_category():
    with pytest.raises(ValidationError):
        Requirement(
            tender_id="test",
            document_id="test",
            category="Security",
            requirement_type="Requirement",
            description="Test requirement",
            mandatory=True,
            source_document="test.pdf",
            pdf_page=1,
            evidence_text="Test evidence",
        )

def test_valid_extraction_result():
    requirement = Requirement(
        tender_id="snoqualmie_erp",
        document_id="rfp_erp",
        category="Technical",
        sub_category="Architecture",
        requirement_type="Requirement",
        description="The solution must support a Microsoft-centric architecture.",
        mandatory=True,
        source_document="RFP-for-ERP-Software-and-Implementation-Services.pdf",
        pdf_page=2,
        page_label="3",
        evidence_text="Microsoft-centric architecture",
    )

    result = ExtractionResult(
        document_id="rfp_erp",
        source_document="RFP-for-ERP-Software-and-Implementation-Services.pdf",
        requirements=[requirement],
    )

    assert result.document_id == "rfp_erp"
    assert len(result.requirements) == 1
    assert result.requirements[0].category == "Technical"


def test_extraction_result_can_be_empty():
    result = ExtractionResult(
        document_id="rfp_erp",
        source_document="RFP-for-ERP-Software-and-Implementation-Services.pdf",
        requirements=[],
    )

    assert result.requirements == []

def test_valid_extracted_requirement():
    requirement = ExtractedRequirement(
        category="Technical",
        sub_category="Security",
        requirement_type="Requirement",
        description="The system must support role-based access control.",
        mandatory=True,
        pdf_page=4,
        page_label="5",
        section="Security Requirements",
        evidence_text="The system must support role-based access control.",
    )

    assert requirement.category == "Technical"
    assert requirement.pdf_page == 4


def test_invalid_extracted_requirement_category():
    with pytest.raises(ValidationError):
        ExtractedRequirement(
            category="Security",
            requirement_type="Requirement",
            description="Test",
            mandatory=True,
            pdf_page=1,
            evidence_text="Test",
        )


def test_llm_extraction_result():
    requirement = ExtractedRequirement(
        category="Technical",
        requirement_type="Requirement",
        description="The system must support encryption.",
        mandatory=True,
        pdf_page=2,
        evidence_text="The system must support encryption.",
    )

    result = LLMExtractionResult(
        requirements=[requirement]
    )

    assert len(result.requirements) == 1
    assert result.requirements[0].mandatory is True