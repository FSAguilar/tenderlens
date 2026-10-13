from src.extraction.pdf_reader import extract_pages


pages = extract_pages(
    "data/raw/RFP-for-ERP-Software-and-Implementation-Services.pdf"
)

print("Pages:", len(pages))

print("\n--- PAGE 1 ---")
print(pages[0]["text"][:1000])