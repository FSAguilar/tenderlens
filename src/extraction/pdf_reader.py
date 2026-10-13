from pathlib import Path

import fitz


def extract_pages(pdf_path: str | Path) -> list[dict]:
    pdf_path = Path(pdf_path)

    if not pdf_path.exists():
        raise FileNotFoundError(f"PDF not found: {pdf_path}")

    document = fitz.open(pdf_path)

    pages = []

    try:
        for page_index, page in enumerate(document):
            pages.append(
                {
                    "pdf_page": page_index + 1,
                    "text": page.get_text("text").strip(),
                }
            )

        return pages

    finally:
        document.close()