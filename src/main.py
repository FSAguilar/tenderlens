from src.extraction.pdf_reader import extract_pages
from src.extraction.requirement_extractor import extract_requirements_from_pages


PDF_PATH = "data/raw/RFP-for-ERP-Software-and-Implementation-Services.pdf"

pages = extract_pages(PDF_PATH)

# Solo la página física 2 para la primera prueba.
test_pages = pages[1:2]

result = extract_requirements_from_pages(
    pages=test_pages,
    tender_id="snoqualmie_erp",
    document_id="snoqualmie_erp_rfp",
    source_document="RFP-for-ERP-Software-and-Implementation-Services.pdf",
)

print(result.model_dump_json(indent=2))