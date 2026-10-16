# TenderLens

**Evidence-based requirement extraction from procurement documents using Azure OpenAI.**

TenderLens is an experimental AI-powered document processing tool designed to extract, classify, and evaluate requirements from Requests for Proposals (RFPs) and tender documents.

The project focuses on a common challenge in procurement: important requirements are often distributed across lengthy documents, making manual extraction time-consuming and difficult to verify.

Rather than generating untraceable summaries, TenderLens structures extracted requirements and associates them with supporting text and source-page references.

## Current Capabilities

- **PDF processing:** Extract page-level text from PDF documents using PyMuPDF.
- **AI-powered extraction:** Use Azure OpenAI to identify requirements and other procurement-related information.
- **Structured outputs:** Validate extracted data with Pydantic models.
- **Requirement classification:** Categorize technical, administrative, legal, financial, eligibility, and other requirements.
- **Evidence tracking:** Include supporting quotations and page references for extracted items.
- **Chunked processing:** Process documents in overlapping page groups.
- **Deduplication:** Remove duplicate items based on normalized evidence and page references.
- **Evaluation:** Compare predictions against manually annotated reference datasets using Precision, Recall, F1, and classification accuracy.

## Technology Stack

| Area | Technology |
|---|---|
| Language | Python 3.12 |
| AI | Azure OpenAI |
| PDF processing | PyMuPDF |
| Data validation | Pydantic |
| Authentication | Azure Identity |
| Containerization | Docker |
| Testing | Pytest |

## Processing Pipeline

```text
PDF Document
     |
     v
Page-level Text Extraction
     |
     v
Overlapping Page Chunks
     |
     v
Azure OpenAI
     |
     v
Structured Requirement Extraction
     |
     v
Pydantic Validation
     |
     v
Deduplication + Requirement IDs
     |
     v
Structured JSON Output
     |
     v
Evaluation Against Gold Datasets
```

## Data Structure

Each extracted requirement includes fields such as:

- Requirement ID
- Tender and document identifiers
- Category and subcategory
- Requirement type
- Description
- Mandatory status
- Source document
- PDF page and page label
- Document section
- Supporting evidence

The system distinguishes between requirements, evaluation criteria, deadlines, and deliverables.

## Evaluation

TenderLens includes manually annotated reference datasets for evaluating extraction quality.

Current evaluation components calculate:

- Precision
- Recall
- F1 score
- Mandatory classification accuracy
- Category classification accuracy
- Requirement type classification accuracy

These metrics support comparisons between extraction runs and help identify missed, incorrectly classified, or unsupported requirements.

## Development Status

**Status: Active development — functional extraction and evaluation prototype.**

The current implementation focuses on a Python-based document extraction pipeline.

Planned improvements include stronger evidence validation, more robust evaluation, configurable execution, improved test coverage, and cloud deployment.

TenderLens is not yet a production-ready procurement compliance platform. Extracted information should be independently verified before being used for procurement decisions.

## Repository Structure

```text
src/
  clients/       Azure OpenAI client
  extraction/    PDF and requirement extraction
  models/        Pydantic schemas
  evaluation/    Evaluation and aggregation

tests/           Automated tests
data/gold/       Reference documents and annotations
docs/            Technical documentation
```

## Running Tests

Build the development environment with Docker Compose:

```bash
docker compose build
```

Execute the test suite:

```bash
docker compose run --rm tenderlens python -m pytest
```

Running document extraction additionally requires Azure configuration, valid authentication, and an input PDF. The current development entry point uses a local file path; a configurable command-line interface is planned.

## Roadmap

- [x] PDF text extraction
- [x] Azure OpenAI integration
- [x] Structured requirement extraction
- [x] Chunked document processing
- [x] Basic deduplication
- [x] Reference dataset evaluation
- [ ] Configurable CLI
- [ ] Deterministic source-evidence verification
- [ ] Expanded evaluation and regression testing
- [ ] Automated CI pipeline
- [ ] Cloud deployment and observability
- [ ] Interactive review interface

## Disclaimer

TenderLens is a personal software engineering project under active development. Its output is intended to assist document review, not replace human judgment or legal and procurement expertise.