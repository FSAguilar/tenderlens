import argparse
import json
from pathlib import Path


def load_evaluation(path: str | Path) -> dict:
    path = Path(path)

    with path.open("r", encoding="utf-8") as file:
        return json.load(file)


def aggregate_evaluations(evaluations: list[dict]) -> dict:
    if not evaluations:
        raise ValueError("At least one evaluation is required.")

    detection_keys = [
        "precision",
        "recall",
        "f1",
    ]

    classification_keys = [
        "mandatory_accuracy",
        "category_accuracy",
        "requirement_type_accuracy",
    ]

    detection = {
        key: sum(
            evaluation["detection"][key]
            for evaluation in evaluations
        ) / len(evaluations)
        for key in detection_keys
    }

    classification = {
        key: sum(
            evaluation["classification"][key]
            for evaluation in evaluations
        ) / len(evaluations)
        for key in classification_keys
    }

    return {
        "datasets": [
            evaluation["dataset"]
            for evaluation in evaluations
        ],
        "dataset_count": len(evaluations),
        "detection_macro_average": detection,
        "classification_macro_average": classification,
    }


def parse_args():
    parser = argparse.ArgumentParser(
        description="Aggregate TenderLens evaluation results."
    )

    parser.add_argument(
        "--evaluations",
        nargs="+",
        required=True,
        help="Evaluation JSON files.",
    )

    parser.add_argument(
        "--output",
        required=True,
        help="Output path for aggregate evaluation.",
    )

    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()

    evaluations = [
        load_evaluation(path)
        for path in args.evaluations
    ]

    result = aggregate_evaluations(evaluations)

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    output_path.write_text(
        json.dumps(
            result,
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    print(json.dumps(result, indent=2))
    print(f"\nSaved to: {output_path}")