from src.clients.azure_openai import get_azure_openai_client
from src.models.requirement import (
    ExtractedRequirement,
    ExtractionResult,
    LLMExtractionResult,
    Requirement,
)

SYSTEM_PROMPT = """
You extract procurement requirements from tender documents.

Return only requirements that are explicitly supported by the source text.

Rules:
- Do not infer or invent requirements.
- Every requirement must include verbatim evidence_text from the source.
- evidence_text must be the minimal sufficient fragment supporting the requirement.
- pdf_page must match the [PDF_PAGE: N] marker containing the evidence.
- mandatory must be:
  - true when the source explicitly imposes an obligation;
  - false when the source explicitly marks something as optional, preferred, or desirable;
  - null when obligation status is ambiguous.
- Use only the allowed categories and requirement types defined by the schema.
- description must normalize the requirement without adding unsupported meaning.
- If no requirement is supported by the text, return an empty requirements list.
"""

def build_paginated_text(pages: list[dict]) -> str:
    sections = []

    for page in pages:
        pdf_page = page["pdf_page"]
        text = page["text"].strip()

        sections.append(
            f"[PDF_PAGE: {pdf_page}]\n{text}"
        )

    return "\n\n".join(sections)




def extract_requirements_from_pages(
    pages: list[dict],
    tender_id: str,
    document_id: str,
    source_document: str,
) -> ExtractionResult:
    if not pages:
        return ExtractionResult(
            document_id=document_id,
            source_document=source_document,
            requirements=[],
        )

    paginated_text = build_paginated_text(pages)

    llm_result = extract_with_llm(paginated_text)

    return build_extraction_result(
        extracted_requirements=llm_result.requirements,
        tender_id=tender_id,
        document_id=document_id,
        source_document=source_document,
    )

def build_extraction_result(
    extracted_requirements: list[ExtractedRequirement],
    tender_id: str,
    document_id: str,
    source_document: str,
) -> ExtractionResult:
    requirements = []

    for index, extracted in enumerate(extracted_requirements, start=1):
        requirements.append(
            Requirement(
                id=f"REQ-{index:03d}",
                tender_id=tender_id,
                document_id=document_id,
                category=extracted.category,
                sub_category=extracted.sub_category,
                requirement_type=extracted.requirement_type,
                description=extracted.description,
                mandatory=extracted.mandatory,
                source_document=source_document,
                pdf_page=extracted.pdf_page,
                page_label=extracted.page_label,
                section=extracted.section,
                evidence_text=extracted.evidence_text,
            )
        )

    return ExtractionResult(
        document_id=document_id,
        source_document=source_document,
        requirements=requirements,
    )


def extract_with_llm(paginated_text: str) -> LLMExtractionResult:
    client = get_azure_openai_client()

    completion = client.beta.chat.completions.parse(
        model="chat-dev",
        messages=[
            {
                "role": "system",
                "content": SYSTEM_PROMPT,
            },
            {
                "role": "user",
                "content": paginated_text,
            },
        ],
        response_format=LLMExtractionResult,
    )

    message = completion.choices[0].message

    if message.refusal:
        raise RuntimeError(
            f"Model refused extraction: {message.refusal}"
        )

    if message.parsed is None:
        raise RuntimeError(
            "Model returned no parsed extraction result."
        )

    return message.parsed