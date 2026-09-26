import csv
import sys
from pathlib import Path
from collections import Counter, defaultdict

# Make project root importable
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from backend.ml_services.model_manager import LocalScamDetector
from backend.url_detection.url_classifier import calculate_risk_score


DATASET = PROJECT_ROOT / "datasets" / "dhokadetect_qa_5000.csv"

FAILED_CASES_FILE = (
    PROJECT_ROOT / "datasets" / "benchmark_failed_cases.csv"
)


def load_dataset():
    with DATASET.open("r", encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def evaluate():

    print("=" * 70)
    print("DhokaDetect — 5,000 Case QA Benchmark")
    print("=" * 70)

    rows = load_dataset()

    print(f"Dataset cases: {len(rows)}")
    print("Loading local NLP model...")
    print()

    detector = LocalScamDetector()

    correct = 0
    false_positives = 0
    false_negatives = 0

    # Store all incorrect predictions for analysis
    failed_cases = []

    category_stats = defaultdict(
        lambda: {
            "total": 0,
            "correct": 0,
            "false_positive": 0,
            "false_negative": 0,
        }
    )

    confusion = Counter()

    print("Running benchmark...")

    for index, row in enumerate(rows, start=1):

        text = row["raw_text"]
        expected = row["expected_risk_level"]
        category = row["scam_category"]

        # -------------------------------------------------
        # NLP prediction
        # -------------------------------------------------

        results, _ = detector.predict([text])
        text_result = results[0]

        text_prediction = text_result["prediction"]
        scam_confidence = text_result["scam_confidence"]
        ml_bert_score = text_result["ml_bert_score"]
        heuristic_score = text_result["heuristic_score"]
        red_flags = text_result["red_flags"]

        # -------------------------------------------------
        # URL prediction
        # -------------------------------------------------

        urls = [
            u.strip()
            for u in row["extracted_urls"].split("|")
            if u.strip()
        ]

        url_risk = 0.0
        url_reasons = []

        for url in urls:

            result = calculate_risk_score(url)

            if result["risk_score"] > url_risk:
                url_risk = result["risk_score"]

            url_reasons.extend(result["reasons"])

        # -------------------------------------------------
        # Final QA prediction
        # -------------------------------------------------
        #
        # Conservative benchmark rule:
        #
        # Text predicts SCAM
        # OR
        # URL risk >= 0.50
        #
        # => HIGH
        # -------------------------------------------------

        if (
            text_prediction == "SCAM"
            or url_risk >= 0.50
        ):
            prediction = "high"
        else:
            prediction = "low"

        # -------------------------------------------------
        # Metrics
        # -------------------------------------------------

        is_correct = prediction == expected

        if is_correct:

            correct += 1
            category_stats[category]["correct"] += 1

        else:

            # ---------------------------------------------
            # Save failed case with full diagnostic data
            # ---------------------------------------------

            failure_type = ""

            if expected == "low" and prediction == "high":

                false_positives += 1
                category_stats[category]["false_positive"] += 1
                failure_type = "FALSE_POSITIVE"

            elif expected == "high" and prediction == "low":

                false_negatives += 1
                category_stats[category]["false_negative"] += 1
                failure_type = "FALSE_NEGATIVE"

            failed_cases.append({
                "case_id": row.get("case_id", ""),
                "raw_text": text,
                "expected": expected,
                "prediction": prediction,
                "failure_type": failure_type,
                "category": category,

                "text_prediction": text_prediction,
                "scam_confidence": scam_confidence,
                "ml_bert_score": ml_bert_score,
                "heuristic_score": heuristic_score,
                "red_flags": " | ".join(red_flags),

                "urls": row.get("extracted_urls", ""),
                "url_risk": round(url_risk, 4),
                "url_reasons": " | ".join(url_reasons),
            })

        category_stats[category]["total"] += 1

        confusion[(expected, prediction)] += 1

        # -------------------------------------------------
        # Progress
        # -------------------------------------------------

        if index % 250 == 0:
            print(f"Processed {index}/{len(rows)} cases...")

    # -------------------------------------------------
    # Overall metrics
    # -------------------------------------------------

    total = len(rows)

    accuracy = correct / total if total else 0

    legitimate_total = sum(
        1
        for row in rows
        if row["expected_risk_level"] == "low"
    )

    scam_total = sum(
        1
        for row in rows
        if row["expected_risk_level"] == "high"
    )

    false_positive_rate = (
        false_positives / legitimate_total
        if legitimate_total
        else 0
    )

    false_negative_rate = (
        false_negatives / scam_total
        if scam_total
        else 0
    )

    true_positives = confusion[("high", "high")]

    predicted_positive = (
        true_positives + false_positives
    )

    precision = (
        true_positives / predicted_positive
        if predicted_positive
        else 0
    )

    recall = (
        true_positives / scam_total
        if scam_total
        else 0
    )

    f1 = (
        2 * precision * recall / (precision + recall)
        if precision + recall
        else 0
    )

    # -------------------------------------------------
    # Print results
    # -------------------------------------------------

    print()
    print("=" * 70)
    print("OVERALL RESULTS")
    print("=" * 70)

    print(f"Total cases       : {total}")
    print(f"Correct           : {correct}")
    print(f"Incorrect         : {total - correct}")
    print(f"Accuracy          : {accuracy:.2%}")

    print()
    print(f"False positives   : {false_positives}")
    print(f"False negatives   : {false_negatives}")
    print(f"FP rate           : {false_positive_rate:.2%}")
    print(f"FN rate           : {false_negative_rate:.2%}")

    print()
    print(f"Scam precision    : {precision:.2%}")
    print(f"Scam recall       : {recall:.2%}")
    print(f"F1 score          : {f1:.2%}")

    # -------------------------------------------------
    # Confusion matrix
    # -------------------------------------------------

    print()
    print("=" * 70)
    print("CONFUSION MATRIX")
    print("=" * 70)

    print()
    print("                  Predicted")
    print("                  LOW       HIGH")

    print(
        f"Actual LOW       "
        f"{confusion[('low', 'low')]:<10}"
        f"{confusion[('low', 'high')]}"
    )

    print(
        f"Actual HIGH      "
        f"{confusion[('high', 'low')]:<10}"
        f"{confusion[('high', 'high')]}"
    )

    # -------------------------------------------------
    # Category results
    # -------------------------------------------------

    print()
    print("=" * 70)
    print("CATEGORY PERFORMANCE")
    print("=" * 70)

    for category in sorted(category_stats):

        stats = category_stats[category]

        total_category = stats["total"]

        accuracy_category = (
            stats["correct"] / total_category
            if total_category
            else 0
        )

        print(
            f"{category:<30} "
            f"{accuracy_category:>7.2%} "
            f"({stats['correct']}/{total_category})"
        )

    # -------------------------------------------------
    # Save failed cases
    # -------------------------------------------------

    print()
    print("=" * 70)
    print("FAILED CASE DIAGNOSTICS")
    print("=" * 70)

    fieldnames = [
        "case_id",
        "raw_text",
        "expected",
        "prediction",
        "failure_type",
        "category",

        "text_prediction",
        "scam_confidence",
        "ml_bert_score",
        "heuristic_score",
        "red_flags",

        "urls",
        "url_risk",
        "url_reasons",
    ]

    with FAILED_CASES_FILE.open(
        "w",
        encoding="utf-8",
        newline=""
    ) as f:

        writer = csv.DictWriter(
            f,
            fieldnames=fieldnames
        )

        writer.writeheader()
        writer.writerows(failed_cases)

    print(f"Failed cases saved : {FAILED_CASES_FILE}")
    print(f"Total failed cases : {len(failed_cases)}")
    print(f"False positives   : {false_positives}")
    print(f"False negatives   : {false_negatives}")

    print()
    print("=" * 70)
    print("Benchmark complete.")
    print("=" * 70)


if __name__ == "__main__":
    evaluate()