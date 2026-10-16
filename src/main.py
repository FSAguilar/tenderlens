# from pathlib import Path

# from src.extraction.pdf_reader import extract_pages
# from src.extraction.requirement_extractor import extract_requirements_from_pages


# PDF_PATH = "data/raw/RFP-for-ERP-Software-and-Implementation-Services.pdf"

# pages = extract_pages(PDF_PATH)

# # Solo página física 2 por ahora
# test_pages = pages[1:2]

# result = extract_requirements_from_pages(
#     pages=test_pages,
#     tender_id="snoqualmie_erp",
#     document_id="snoqualmie_erp_rfp",
#     source_document="RFP-for-ERP-Software-and-Implementation-Services.pdf",
# )

# output_path = Path("outputs/snoqualmie_page_2_baseline.json")
# output_path.parent.mkdir(parents=True, exist_ok=True)

# output_path.write_text(
#     result.model_dump_json(indent=2),
#     encoding="utf-8",
# )

# print(result.model_dump_json(indent=2))
# print(f"\nSaved to: {output_path}")

# # from pathlib import Path

# # from src.extraction.pdf_reader import extract_pages
# # from src.extraction.requirement_extractor import extract_requirements_from_pages


# # PDF_PATH = "data/raw/RFP-2026-3-IT-SERVICES.pdf"

# # pages = extract_pages(PDF_PATH)

# # # Página física 4
# # test_pages = pages[3:4]

# # result = extract_requirements_from_pages(
# #     pages=test_pages,
# #     tender_id="tender_KINGSBURY_IT",
# #     document_id="kingsbury_it_managed_services",
# #     source_document="RFP-2026-3-IT-SERVICES.pdf",
# # )

# # output_path = Path("outputs/kingsbury_page_4_baseline.json")
# # output_path.parent.mkdir(parents=True, exist_ok=True)

# # output_path.write_text(
# #     result.model_dump_json(indent=2),
# #     encoding="utf-8",
# # )

# # print(result.model_dump_json(indent=2))
# # print(f"\nSaved to: {output_path}")

from pathlib import Path

from src.extraction.pdf_reader import extract_pages
from src.extraction.requirement_extractor import (
    extract_requirements_from_document,
)


PDF_PATH = "data/raw/RFP-2026-3-IT-SERVICES.pdf"

pages = extract_pages(PDF_PATH)

# Primera prueba multichunk: páginas físicas 1-4
test_pages = pages[3:4]

# result = extract_requirements_from_document(
#     pages=test_pages,
#     tender_id="tender_KINGSBURY_IT",
#     document_id="kingsbury_it_managed_services",
#     source_document="RFP-2026-3-IT-SERVICES.pdf",
#     chunk_size=2,
#     overlap=1,
# )
result = extract_requirements_from_document(
    pages=test_pages,
    tender_id="tender_KINGSBURY_IT",
    document_id="kingsbury_it_managed_services",
    source_document="RFP-2026-3-IT-SERVICES.pdf",
    chunk_size=2,
    overlap=0,
)


output_path = Path(
    "outputs/kingsbury_page_4_current.json"
)

output_path.parent.mkdir(
    parents=True,
    exist_ok=True,
)

output_path.write_text(
    result.model_dump_json(indent=2),
    encoding="utf-8",
)

print(f"Pages processed: {len(test_pages)}")
print(f"Requirements extracted: {len(result.requirements)}")
print(f"Saved to: {output_path}")