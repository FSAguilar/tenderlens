from src.extraction.pdf_reader import extract_pages


def test_extract_pages():
    pages = extract_pages(
        "data/raw/RFP-for-ERP-Software-and-Implementation-Services.pdf"
    )

    assert len(pages) > 0
    assert pages[0]["pdf_page"] == 1
    assert isinstance(pages[0]["text"], str)