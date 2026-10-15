import pytest

from src.extraction.requirement_extractor import (
    build_extraction_result,
    build_paginated_text,
    extract_requirements_from_pages,
)
from unittest.mock import patch

from src.models.requirement import (
    ExtractedRequirement,
    LLMExtractionResult,
)



def test_empty_pages_returns_empty_result():
    result = extract_requirements_from_pages(
        pages=[],
        tender_id="test_tender",
        document_id="test_document",
        source_document="test.pdf",
    )

    assert result.document_id == "test_document"
    assert result.source_document == "test.pdf"
    assert result.requirements == []


# def test_non_empty_pages_not_implemented_yet():
#     pages = [
#         {
#             "pdf_page": 1,
#             "text": "The system must support role-based access control.",
#         }
#     ]

#     with pytest.raises(NotImplementedError):
#         extract_requirements_from_pages(
#             pages=pages,
#             document_id="test_document",
#             source_document="test.pdf",
#         )

def test_build_paginated_text():
    pages = [
        {
            "pdf_page": 1,
            "text": "First page content.",
        },
        {
            "pdf_page": 2,
            "text": "Second page content.",
        },
    ]

    result = build_paginated_text(pages)

    assert "[PDF_PAGE: 1]" in result
    assert "First page content." in result
    assert "[PDF_PAGE: 2]" in result
    assert "Second page content." in result


def test_build_extraction_result():
    extracted = ExtractedRequirement(
        category="Technical",
        sub_category="Security",
        requirement_type="Requirement",
        description="The system must support encryption.",
        mandatory=True,
        pdf_page=2,
        evidence_text="The system must support encryption.",
    )

    result = build_extraction_result(
        extracted_requirements=[extracted],
        tender_id="tender_001",
        document_id="document_001",
        source_document="test.pdf",
    )

    assert len(result.requirements) == 1

    requirement = result.requirements[0]

    assert requirement.id == "REQ-001"
    assert requirement.tender_id == "tender_001"
    assert requirement.document_id == "document_001"
    assert requirement.source_document == "test.pdf"
    assert requirement.category == "Technical"

def test_extract_requirements_from_pages():
    pages = [
        {
            "pdf_page": 1,
            "text": "The system must support role-based access control.",
        }
    ]

    fake_llm_result = LLMExtractionResult(
        requirements=[
            ExtractedRequirement(
                category="Technical",
                sub_category="Security",
                requirement_type="Requirement",
                description="The system must support role-based access control.",
                mandatory=True,
                pdf_page=1,
                evidence_text="The system must support role-based access control.",
            )
        ]
    )

    with patch(
        "src.extraction.requirement_extractor.extract_with_llm",
        return_value=fake_llm_result,
    ):
        result = extract_requirements_from_pages(
            pages=pages,
            tender_id="test_tender",
            document_id="test_document",
            source_document="test.pdf",
        )

    assert len(result.requirements) == 1

    requirement = result.requirements[0]

    assert requirement.id == "REQ-001"
    assert requirement.tender_id == "test_tender"
    assert requirement.category == "Technical"
    assert requirement.pdf_page == 1