import json
import argparse
import re
from pathlib import Path
import json
from pathlib import Path

def normalize_text(text: str) -> str:
    text = text.lower()
    text = re.sub(r"\s+", " ", text)
    text = re.sub(r"[^\w\s]", "", text)

    return text.strip()

def parse_args():
    parser = argparse.ArgumentParser(
        description="Evaluate TenderLens predictions against a gold dataset."
    )

    parser.add_argument(
        "--gold",
        required=True,
        help="Path to the gold JSON file.",
    )

    parser.add_argument(
        "--predictions",
        required=True,
        help="Path to the predictions JSON file.",
    )

    parser.add_argument(
        "--dataset",
        required=True,
        help="Dataset name used in the evaluation output.",
    )

    parser.add_argument(
        "--output",
        required=True,
        help="Path where the evaluation JSON will be saved.",
    )

    parser.add_argument(
    "--pdf-page",
    type=int,
    default=None,
    help="Evaluate only requirements from a specific physical PDF page.",
)

    return parser.parse_args()

def evidence_matches(gold_evidence: str, predicted_evidence: str) -> bool:
    gold = normalize_text(gold_evidence)
    predicted = normalize_text(predicted_evidence)

    return (
        gold == predicted
        or gold in predicted
        or predicted in gold
    )


def load_requirements(path: str | Path) -> list[dict]:
    path = Path(path)

    with path.open("r", encoding="utf-8") as file:
        data = json.load(file)

    # Prediction files have {"requirements": [...]}
    if isinstance(data, dict) and "requirements" in data:
        return data["requirements"]

    # Gold dataset is currently a top-level list
    if isinstance(data, list):
        return data

    raise ValueError(f"Unsupported requirement file format: {path}")

def match_requirements(
    gold_requirements: list[dict],
    predicted_requirements: list[dict],
) -> list[tuple[dict, dict]]:
    matches = []
    used_predictions = set()

    for gold in gold_requirements:
        for index, predicted in enumerate(predicted_requirements):
            if index in used_predictions:
                continue

            if evidence_matches(
                gold["evidence_text"],
                predicted["evidence_text"],
            ):
                matches.append((gold, predicted))
                used_predictions.add(index)
                break

    return matches

def calculate_metrics(
    gold_requirements: list[dict],
    predicted_requirements: list[dict],
) -> dict:
    matches = match_requirements(
        gold_requirements,
        predicted_requirements,
    )

    true_positives = len(matches)
    false_positives = len(predicted_requirements) - true_positives
    false_negatives = len(gold_requirements) - true_positives

    precision = (
        true_positives / len(predicted_requirements)
        if predicted_requirements
        else 0.0
    )

    recall = (
        true_positives / len(gold_requirements)
        if gold_requirements
        else 0.0
    )

    f1 = (
        2 * precision * recall / (precision + recall)
        if precision + recall
        else 0.0
    )

    return {
        "true_positives": true_positives,
        "false_positives": false_positives,
        "false_negatives": false_negatives,
        "precision": precision,
        "recall": recall,
        "f1": f1,
    }

def filter_gold(
    requirements: list[dict],
    source_document: str,
    pdf_page: int,
) -> list[dict]:
    return [
        requirement
        for requirement in requirements
        if requirement["source_document"] == source_document
        and requirement["pdf_page"] == pdf_page
    ]

def get_unmatched_predictions(
    gold_requirements: list[dict],
    predicted_requirements: list[dict],
) -> list[dict]:
    matches = match_requirements(
        gold_requirements,
        predicted_requirements,
    )

    matched_prediction_ids = {
        id(predicted)
        for _, predicted in matches
    }

    return [
        predicted
        for predicted in predicted_requirements
        if id(predicted) not in matched_prediction_ids
    ]


def calculate_classification_accuracy(
    matches: list[tuple[dict, dict]],
) -> dict:
    if not matches:
        return {
            "mandatory_accuracy": 0.0,
            "category_accuracy": 0.0,
            "requirement_type_accuracy": 0.0,
        }

    mandatory_correct = 0
    category_correct = 0
    requirement_type_correct = 0

    for gold, predicted in matches:
        if gold["mandatory"] == predicted["mandatory"]:
            mandatory_correct += 1

        if gold["category"] == predicted["category"]:
            category_correct += 1

        if gold["requirement_type"] == predicted["requirement_type"]:
            requirement_type_correct += 1

    total = len(matches)

    return {
        "mandatory_accuracy": mandatory_correct / total,
        "category_accuracy": category_correct / total,
        "requirement_type_accuracy": requirement_type_correct / total,
    }

def print_classification_errors(
    matches: list[tuple[dict, dict]],
) -> None:
    print("\nCLASSIFICATION ERRORS")
    print("---------------------")

    for gold, predicted in matches:
        errors = []

        if gold["mandatory"] != predicted["mandatory"]:
            errors.append(
                f"mandatory: gold={gold['mandatory']} "
                f"predicted={predicted['mandatory']}"
            )

        if gold["category"] != predicted["category"]:
            errors.append(
                f"category: gold={gold['category']} "
                f"predicted={predicted['category']}"
            )

        if gold["requirement_type"] != predicted["requirement_type"]:
            errors.append(
                f"type: gold={gold['requirement_type']} "
                f"predicted={predicted['requirement_type']}"
            )

        if not errors:
            continue

        print(f"\nGOLD: {gold['description']}")
        print(f"PRED: {predicted['description']}")

        for error in errors:
            print(f"- {error}")

def get_unmatched_gold(
    gold_requirements: list[dict],
    predicted_requirements: list[dict],
) -> list[dict]:
    matches = match_requirements(
        gold_requirements,
        predicted_requirements,
    )

    matched_gold_ids = {
        id(gold)
        for gold, _ in matches
    }

    return [
        gold
        for gold in gold_requirements
        if id(gold) not in matched_gold_ids
    ]

# if __name__ == "__main__":
    # gold = load_requirements(
    #     "data/gold/exhaustive/snoqualmie_page_2_v0.1.json"
    # )

    # predictions = load_requirements(
    #     "outputs/snoqualmie_page_2_baseline.json"
    # )

    # # gold = filter_gold(
    # #     gold,
    # #     source_document="RFP-for-ERP-Software-and-Implementation-Services.pdf",
    # #     pdf_page=2,
    # # )

    # metrics = calculate_metrics(
    #     gold_requirements=gold,
    #     predicted_requirements=predictions,
    # )

    # print(f"Gold requirements: {len(gold)}")
    # print(f"Predicted requirements: {len(predictions)}")
    # print()

    # print(f"True positives:  {metrics['true_positives']}")
    # print(f"False positives: {metrics['false_positives']}")
    # print(f"False negatives: {metrics['false_negatives']}")
    # print()

    # print(f"Precision: {metrics['precision']:.3f}")
    # print(f"Recall:    {metrics['recall']:.3f}")
    # print(f"F1:        {metrics['f1']:.3f}")

    # unmatched = get_unmatched_predictions(
    #     gold,
    #     predictions,
    # )

    # print("\nUNMATCHED PREDICTIONS")
    # print("---------------------")

    # for requirement in unmatched:
    #     print(
    #         f"[{requirement['requirement_type']}] "
    #         f"{requirement['description']}"
    #     )
    #     print(f"Evidence: {requirement['evidence_text']}")
    #     print()

    # matches = match_requirements(
    #     gold,
    #     predictions,
    # )

    # classification_metrics = calculate_classification_accuracy(matches)

    # print()
    # print("CLASSIFICATION")
    # print("--------------")
    # print(
    #     f"Mandatory accuracy:       "
    #     f"{classification_metrics['mandatory_accuracy']:.3f}"
    # )
    # print(
    #     f"Category accuracy:        "
    #     f"{classification_metrics['category_accuracy']:.3f}"
    # )
    # print(
    #     f"Requirement type accuracy:"
    #     f" {classification_metrics['requirement_type_accuracy']:.3f}"
    # )

    # print_classification_errors(matches)


    # unmatched_gold = get_unmatched_gold(
    #     gold,
    #     predictions,
    # )

    # print("\nMISSED GOLD")
    # print("-----------")

    # for requirement in unmatched_gold:
    #     print(
    #         f"[{requirement['requirement_type']}] "
    #         f"{requirement['description']}"
    #     )
    #     print(f"Evidence: {requirement['evidence_text']}")
    #     print()

    # evaluation_result = {
    #     "dataset": "snoqualmie_page_2_v0.1.json",
    #     "detection": {
    #         "true_positives": metrics["true_positives"],
    #         "false_positives": metrics["false_positives"],
    #         "false_negatives": metrics["false_negatives"],
    #         "precision": metrics["precision"],
    #         "recall": metrics["recall"],
    #         "f1": metrics["f1"],
    #     },
    #     "classification": {
    #         "mandatory_accuracy": classification_metrics["mandatory_accuracy"],
    #         "category_accuracy": classification_metrics["category_accuracy"],
    #         "requirement_type_accuracy": classification_metrics[
    #             "requirement_type_accuracy"
    #         ],
    #     },
    #     "missed_gold_count": len(unmatched_gold),
    #     "unmatched_prediction_count": len(unmatched),
    # }

    # output_path = Path(
    #     "outputs/evaluations/snoqualmie_page_2_v0.1.json"
    # )

    # output_path.parent.mkdir(
    #     parents=True,
    #     exist_ok=True,
    # )

    # output_path.write_text(
    #     json.dumps(
    #         evaluation_result,
    #         indent=2,
    #         ensure_ascii=False,
    #     ),
    #     encoding="utf-8",
    # )

    # print(f"\nEvaluation saved to: {output_path}")

def filter_by_pdf_page(
    requirements: list[dict],
    pdf_page: int | None,
) -> list[dict]:
    if pdf_page is None:
        return requirements

    return [
        requirement
        for requirement in requirements
        if requirement["pdf_page"] == pdf_page
    ]

if __name__ == "__main__":
    args = parse_args()

    gold = load_requirements(args.gold)
    predictions = load_requirements(args.predictions)


    gold = filter_by_pdf_page(
        gold,
        args.pdf_page,
    )

    predictions = filter_by_pdf_page(
        predictions,
        args.pdf_page,
    )

    metrics = calculate_metrics(
        gold_requirements=gold,
        predicted_requirements=predictions,
    )

    matches = match_requirements(
        gold,
        predictions,
    )

    classification_metrics = calculate_classification_accuracy(matches)

    unmatched_gold = get_unmatched_gold(
        gold,
        predictions,
    )

    unmatched_predictions = get_unmatched_predictions(
        gold,
        predictions,
    )

    print(f"Gold requirements: {len(gold)}")
    print(f"Predicted requirements: {len(predictions)}")
    print()

    print(f"True positives:  {metrics['true_positives']}")
    print(f"False positives: {metrics['false_positives']}")
    print(f"False negatives: {metrics['false_negatives']}")
    print()

    print(f"Precision: {metrics['precision']:.3f}")
    print(f"Recall:    {metrics['recall']:.3f}")
    print(f"F1:        {metrics['f1']:.3f}")

    print("\nUNMATCHED PREDICTIONS")
    print("---------------------")

    for requirement in unmatched_predictions:
        print(
            f"[{requirement['requirement_type']}] "
            f"{requirement['description']}"
        )
        print(f"Evidence: {requirement['evidence_text']}")
        print()

    print("\nMISSED GOLD")
    print("-----------")

    for requirement in unmatched_gold:
        print(
            f"[{requirement['requirement_type']}] "
            f"{requirement['description']}"
        )
        print(f"Evidence: {requirement['evidence_text']}")
        print()

    print("\nCLASSIFICATION")
    print("--------------")
    print(
        f"Mandatory accuracy:        "
        f"{classification_metrics['mandatory_accuracy']:.3f}"
    )
    print(
        f"Category accuracy:         "
        f"{classification_metrics['category_accuracy']:.3f}"
    )
    print(
        f"Requirement type accuracy: "
        f"{classification_metrics['requirement_type_accuracy']:.3f}"
    )

    print_classification_errors(matches)

    evaluation_result = {
        "dataset": args.dataset,
        "detection": metrics,
        "classification": classification_metrics,
        "missed_gold_count": len(unmatched_gold),
        "unmatched_prediction_count": len(unmatched_predictions),
    }

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    output_path.write_text(
        json.dumps(
            evaluation_result,
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    print(f"\nEvaluation saved to: {output_path}")

