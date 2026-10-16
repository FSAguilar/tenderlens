# tenderlens


tenderlens/
├── README.md
├── docs/
│   ├── product-scope.md
│   ├── requirement-schema.md
│   └── evaluation.md
├── data/
│   ├── raw/
│   │   ├── tender_001/
│   │   ├── tender_002/
│   │   └── ...
│   └── gold/
│       └── requirements.json
├── src/
├── tests/
├── .gitignore
└── pyproject.toml

Python 3.12
Debian slim

docker compose run --rm tenderlens python -m pytest


Extract only requirements that are explicitly supported by the source text.

For every extracted requirement:
- quote the minimal sufficient evidence_text verbatim
- assign the exact PDF_PAGE marker where the evidence appears
- do not infer requirements not explicitly stated
- if mandatory status is ambiguous, return null
- use only the allowed categories and requirement types


LLM
↓
ExtractedRequirement
   category
   sub_category
   requirement_type
   description
   mandatory
   pdf_page
   page_label
   section
   evidence_text
↓
nuestro código añade metadata
↓
Requirement

python -c "from src.clients.azure_openai import get_azure_openai_client; print(get_azure_openai_client())"

python -m src.evaluation.baseline \
  --gold data/gold/exhaustive/snoqualmie_page_2_v0.1.json \
  --predictions outputs/snoqualmie_page_2_baseline.json \
  --dataset snoqualmie_page_2_v0.1 \
  --output outputs/evaluations/snoqualmie_page_2_v0.1.json