from src.evaluation.baseline import (
    calculate_metrics,
    evidence_matches,
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