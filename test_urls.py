import json
from url_detection.url_classifier import calculate_risk_score


DATASET_PATH = "datasets/scam_test_cases.json"

LEGITIMATE_URLS = [
    "https://www.google.com",
    "https://www.sbi.co.in"
]


def main():
    with open(DATASET_PATH, "r", encoding="utf-8") as file:
        dataset = json.load(file)

    total = 0
    correct = 0

    print("URL Dataset Test")
    print("----------------")

    # Test malicious URLs from dataset
    for case in dataset["cases"]:
        url_data = case["input"]["url"]

        if not url_data["available"]:
            continue

        url = url_data["value"]
        expected_label = case["ground_truth"]["modalities"]["url"]

        result = calculate_risk_score(url)
        risk_score = result["risk_score"]

        predicted_label = (
            "malicious" if risk_score >= 0.5 else "benign"
        )

        is_correct = predicted_label == expected_label

        if is_correct:
            correct += 1

        total += 1

        status = "PASS" if is_correct else "FAIL"

        print(
            f"{case['case_id']} | "
            f"{status} | "
            f"Expected: {expected_label} | "
            f"Predicted: {predicted_label} | "
            f"Score: {risk_score}"
        )

    # Test legitimate URLs
    print()
    print("Legitimate URL Tests")
    print("--------------------")

    for url in LEGITIMATE_URLS:
        expected_label = "benign"

        result = calculate_risk_score(url)
        risk_score = result["risk_score"]

        predicted_label = (
            "malicious" if risk_score >= 0.5 else "benign"
        )

        is_correct = predicted_label == expected_label

        if is_correct:
            correct += 1

        total += 1

        status = "PASS" if is_correct else "FAIL"

        print(
            f"LEGITIMATE | {status} | "
            f"Expected: {expected_label} | "
            f"Predicted: {predicted_label} | "
            f"Score: {risk_score} | "
            f"URL: {url}"
        )

    print()
    print("----------------")

    if total > 0:
        accuracy = (correct / total) * 100

        print(f"Correct: {correct}/{total}")
        print(f"Accuracy: {accuracy:.2f}%")
    else:
        print("No test cases found.")


if __name__ == "__main__":
    main()