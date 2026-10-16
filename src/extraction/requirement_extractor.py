from src.clients.azure_openai import get_azure_openai_client
from src.models.requirement import (
    ExtractedRequirement,
    ExtractionResult,
    LLMExtractionResult,
    Requirement,
)
import re
SYSTEM_PROMPT = """
You extract procurement requirements from tender documents.

Return only requirements that are explicitly supported by the source text.

GENERAL RULES:
- Do not infer or invent requirements.
- Every extracted item must include verbatim evidence_text from the source.
- evidence_text must be the minimal sufficient fragment supporting the item.
- pdf_page must match the [PDF_PAGE: N] marker containing the evidence.
- description may normalize the source wording, but must not add unsupported meaning.
- If no supported item exists, return an empty requirements list.

MANDATORY RULES:
- mandatory = true when the source explicitly imposes an obligation,
  responsibility, condition, or required capability.
- mandatory = false only when the source explicitly states that something is
  optional, preferred, desirable, recommended, or otherwise non-mandatory.
- mandatory = null when obligation status cannot be determined.
- EvaluationCriterion items should normally have mandatory = null because they
  describe how proposals are evaluated rather than whether an obligation exists.
- Do not assign mandatory = false merely because something is an evaluation
  factor.

REQUIREMENT TYPE RULES:
- Requirement:
  an obligation, condition, qualification, capability, responsibility, or
  explicit preference imposed on the solution, vendor, or proposal.
- EvaluationCriterion:
  a factor explicitly used to evaluate, compare, score, rank, or select
  proposals/vendors.
- Deadline:
  an explicit date, time, duration, or submission deadline.
- Deliverable:
  an explicit artifact, document, report, file, plan, or other concrete output
  that must be submitted or provided.
- Do not classify an implementation activity or general vendor responsibility
  as Deliverable unless the source explicitly requires a concrete output.

CATEGORY RULES:
- Technical:
  software capabilities, architecture, interoperability, integrations,
  security, performance, infrastructure, usability, or other technical
  characteristics of the solution.

- Eligibility:
  vendor qualifications, prior experience, customer base, references,
  certifications, installed base, organizational qualifications, or
  conditions determining vendor suitability.

- Administrative:
  procurement process, project approach, implementation responsibilities,
  submission process, governance, contract administration, or procedural
  requirements.

- Legal:
  legal obligations, contractual terms, regulatory requirements, licenses,
  liability, or legal compliance.

- Financial:
  price, cost, fees, budget, financial capacity, maintenance costs, or other
  monetary considerations.

- Deadline:
  dates, deadlines, schedules, or explicit timing constraints.

- Deliverable:
  concrete artifacts or outputs that must be produced or submitted.

- Other:
  use only when none of the categories above reasonably applies.

IMPORTANT:
Category and requirement_type describe different dimensions.

For example:
- A customer-reference evaluation factor can be:
  category = Eligibility
  requirement_type = EvaluationCriterion

- A software-integration evaluation factor can be:
  category = Technical
  requirement_type = EvaluationCriterion

- A price evaluation factor can be:
  category = Financial
  requirement_type = EvaluationCriterion

Do not use Other merely because requirement_type is EvaluationCriterion.

- Explicit preferences concerning vendor structure, qualifications, or solution characteristics
  should be classified as Requirement with mandatory = false, unless the source explicitly
  states that the item is used to score or compare proposals.

- Vendor implementation track record, implementation methodology, and prior implementation
  success should be categorized as Eligibility when they are used to assess vendor suitability
  or experience.

- Compliance with procurement or contract terms and conditions should be categorized as
  Administrative unless the source refers to a specific legal, statutory, regulatory,
  licensing, liability, or legal compliance obligation.

  GRANULARITY RULES:
- Extract requirements at the smallest meaningful actionable level.
- When a parent statement only introduces a list of required items, extract the
  individual items and do not also extract the parent as a separate requirement.
- Keep the parent only when it contains an additional independent obligation
  not fully represented by the child items.
- Do not merge distinct obligations merely because they appear in the same section.
"""

def normalize_evidence(text: str) -> str:
    text = text.lower()
    text = re.sub(r"\s+", " ", text)
    text = re.sub(r"[^\w\s]", "", text)

    return text.strip()


def deduplicate_requirements(
    requirements: list[Requirement],
) -> list[Requirement]:
    unique_requirements = []
    seen = set()

    for requirement in requirements:
        key = (
            requirement.pdf_page,
            normalize_evidence(requirement.evidence_text),
        )

        if key in seen:
            continue

        seen.add(key)
        unique_requirements.append(requirement)

    return unique_requirements

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

def chunk_pages(
    pages: list[dict],
    chunk_size: int = 2,
    overlap: int = 0,
) -> list[list[dict]]:
    if chunk_size <= 0:
        raise ValueError("chunk_size must be greater than 0")

    if overlap < 0:
        raise ValueError("overlap cannot be negative")

    if overlap >= chunk_size:
        raise ValueError("overlap must be smaller than chunk_size")

    chunks = []
    step = chunk_size - overlap
    start = 0

    while start < len(pages):
        chunk = pages[start:start + chunk_size]

        if not chunk:
            break

        chunks.append(chunk)

        if start + chunk_size >= len(pages):
            break

        start += step

    return chunks

def extract_requirements_from_document(
    pages: list[dict],
    tender_id: str,
    document_id: str,
    source_document: str,
    chunk_size: int = 2,
    overlap: int = 0,
) -> ExtractionResult:
    all_requirements = []

    chunks = chunk_pages(
        pages,
        chunk_size=chunk_size,
        overlap=overlap,
    )

    for chunk in chunks:
        paginated_text = build_paginated_text(chunk)

        llm_result = extract_with_llm(
            paginated_text
        )

        partial_result = build_extraction_result(
            extracted_requirements=llm_result.requirements,
            tender_id=tender_id,
            document_id=document_id,
            source_document=source_document,
        )

        all_requirements.extend(
            partial_result.requirements
        )

    all_requirements = assign_requirement_ids(
        all_requirements
    )

    # print("Before deduplication:", len(all_requirements))

    all_requirements = deduplicate_requirements(all_requirements)

    # print("After deduplication:", len(all_requirements))

    all_requirements = assign_requirement_ids(
        all_requirements
    )

    return ExtractionResult(
        document_id=document_id,
        source_document=source_document,
        requirements=all_requirements,
    )

def assign_requirement_ids(
    requirements: list[Requirement],
) -> list[Requirement]:
    result = []

    for index, requirement in enumerate(
        requirements,
        start=1,
    ):
        result.append(
            requirement.model_copy(
                update={
                    "id": f"REQ-{index:03d}"
                }
            )
        )

    return result