from src.evaluation.baseline import (
    calculate_metrics,
    evidence_matches,
    filter_by_pdf_page,
    normalize_text,
)


def test_normalize_text():
    result = normalize_text(
        "The SYSTEM must work."
    )

    assert result == "the system must work"


def test_evidence_matches_exact():
    assert evidence_matches(
        "The system must support encryption.",
        "The system must support encryption.",
    )


def test_evidence_matches_containment():
    assert evidence_matches(
        "support encryption",
        "The system must support encryption.",
    )


def test_calculate_metrics():
    gold = [
        {
            "evidence_text": "Requirement A"
        },
        {
            "evidence_text": "Requirement B"
        },
    ]

    predictions = [
        {
            "evidence_text": "Requirement A"
        },
        {
            "evidence_text": "Requirement C"
        },
    ]

    metrics = calculate_metrics(
        gold,
        predictions,
    )

    assert metrics["true_positives"] == 1
    assert metrics["false_positives"] == 1
    assert metrics["false_negatives"] == 1
    assert metrics["precision"] == 0.5
    assert metrics["recall"] == 0.5
    assert metrics["f1"] == 0.5

def test_filter_by_pdf_page():
    requirements = [
        {"pdf_page": 2},
        {"pdf_page": 4},
        {"pdf_page": 4},
    ]

    result = filter_by_pdf_page(
        requirements,
        pdf_page=4,
    )

    assert len(result) == 2
    assert all(
        requirement["pdf_page"] == 4
        for requirement in result
    )

def test_filter_by_pdf_page_none():
    requirements = [
        {"pdf_page": 1},
        {"pdf_page": 2},
    ]

    result = filter_by_pdf_page(
        requirements,
        pdf_page=None,
    )

    assert result == requirements