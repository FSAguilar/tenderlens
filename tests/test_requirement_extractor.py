import pytest

from src.extraction.requirement_extractor import (
    assign_requirement_ids,
    build_extraction_result,
    build_paginated_text,
    deduplicate_requirements,
    extract_requirements_from_pages,
    extract_requirements_from_document,
    chunk_pages
)
from unittest.mock import patch

from src.models.requirement import (
    ExtractedRequirement,
    LLMExtractionResult,
    Requirement,
)
from unittest.mock import patch


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


def test_chunk_pages():
    pages = [
        {"pdf_page": 1, "text": "Page 1"},
        {"pdf_page": 2, "text": "Page 2"},
        {"pdf_page": 3, "text": "Page 3"},
        {"pdf_page": 4, "text": "Page 4"},
        {"pdf_page": 5, "text": "Page 5"},
    ]

    chunks = chunk_pages(
        pages,
        chunk_size=2,
    )

    assert len(chunks) == 3

    assert [
        page["pdf_page"]
        for page in chunks[0]
    ] == [1, 2]

    assert [
        page["pdf_page"]
        for page in chunks[1]
    ] == [3, 4]

    assert [
        page["pdf_page"]
        for page in chunks[2]
    ] == [5]


def test_assign_requirement_ids():
    requirements = [
        Requirement(
            tender_id="test",
            document_id="doc",
            category="Technical",
            requirement_type="Requirement",
            description="A",
            mandatory=True,
            source_document="test.pdf",
            pdf_page=1,
            evidence_text="A",
        ),
        Requirement(
            tender_id="test",
            document_id="doc",
            category="Technical",
            requirement_type="Requirement",
            description="B",
            mandatory=True,
            source_document="test.pdf",
            pdf_page=2,
            evidence_text="B",
        ),
    ]

    result = assign_requirement_ids(
        requirements
    )

    assert result[0].id == "REQ-001"
    assert result[1].id == "REQ-002"

def test_deduplicate_requirements():
    requirement_a = Requirement(
        tender_id="test",
        document_id="doc",
        category="Technical",
        requirement_type="Requirement",
        description="The system must support encryption.",
        mandatory=True,
        source_document="test.pdf",
        pdf_page=2,
        evidence_text="The system must support encryption.",
    )

    requirement_b = Requirement(
        tender_id="test",
        document_id="doc",
        category="Technical",
        requirement_type="Requirement",
        description="The system must support encryption.",
        mandatory=True,
        source_document="test.pdf",
        pdf_page=2,
        evidence_text="THE SYSTEM must support encryption.",
    )

    result = deduplicate_requirements(
        [requirement_a, requirement_b]
    )

    assert len(result) == 1




def test_extract_requirements_from_document():
    pages = [
        {"pdf_page": 1, "text": "Page 1"},
        {"pdf_page": 2, "text": "Page 2"},
        {"pdf_page": 3, "text": "Page 3"},
    ]

    first_llm_result = LLMExtractionResult(
        requirements=[
            ExtractedRequirement(
                category="Technical",
                requirement_type="Requirement",
                description="Requirement A",
                mandatory=True,
                pdf_page=1,
                evidence_text="Requirement A",
            )
        ]
    )

    second_llm_result = LLMExtractionResult(
        requirements=[
            ExtractedRequirement(
                category="Technical",
                requirement_type="Requirement",
                description="Requirement B",
                mandatory=True,
                pdf_page=3,
                evidence_text="Requirement B",
            )
        ]
    )

    with patch(
        "src.extraction.requirement_extractor.extract_with_llm",
        side_effect=[
            first_llm_result,
            second_llm_result,
        ],
    ) as mocked_llm:
        result = extract_requirements_from_document(
            pages=pages,
            tender_id="test_tender",
            document_id="test_document",
            source_document="test.pdf",
            chunk_size=2,
        )

    assert mocked_llm.call_count == 2

    assert len(result.requirements) == 2

    assert result.requirements[0].id == "REQ-001"
    assert result.requirements[1].id == "REQ-002"

    assert result.requirements[0].description == "Requirement A"
    assert result.requirements[1].description == "Requirement B"

def test_chunk_pages_with_overlap():
    pages = [
        {"pdf_page": 1, "text": "Page 1"},
        {"pdf_page": 2, "text": "Page 2"},
        {"pdf_page": 3, "text": "Page 3"},
        {"pdf_page": 4, "text": "Page 4"},
    ]

    chunks = chunk_pages(
        pages,
        chunk_size=2,
        overlap=1,
    )

    assert [
    [page["pdf_page"] for page in chunk]
    for chunk in chunks
] == [
    [1, 2],
    [2, 3],
    [3, 4],
]