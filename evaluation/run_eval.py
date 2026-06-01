import json
from pathlib import Path


GROUND_TRUTH_DIR = Path("output/ground_truth")
EXTRACTED_DIR = Path("data/extracted")


QUESTIONS = {
    "What is the diagnosis?": "diagnosis",
    "Who is the doctor?": "doctor",
    "What medication was prescribed?": "medication",
}


def load_json(file_path: Path) -> dict:
    with file_path.open("r", encoding="utf-8") as f:
        return json.load(f)


def simple_extract_answer(text: str, field_name: str) -> str:
    lines = text.splitlines()
    target = field_name.lower().replace("_", " ")

    for line in lines:
        lower_line = line.lower()
        if target in lower_line:
            parts = line.split(":", 1)
            if len(parts) == 2:
                return parts[1].strip()

    return "Not found in document"


def evaluate_document(ground_truth_file: Path) -> list[dict]:
    gt = load_json(ground_truth_file)
    document_id = gt["document_id"]

    extracted_file = EXTRACTED_DIR / f"{document_id}.txt"
    if not extracted_file.exists():
        return [{
            "document_id": document_id,
            "question": "ALL",
            "expected": "N/A",
            "predicted": "Missing extracted file",
            "correct": False,
        }]

    extracted_text = extracted_file.read_text(encoding="utf-8")

    results = []
    expected_fields = gt.get("expected_fields", {})

    for question, field_name in QUESTIONS.items():
        expected = expected_fields.get(field_name, "N/A")
        predicted = simple_extract_answer(extracted_text, field_name)

        results.append({
            "document_id": document_id,
            "question": question,
            "expected": expected,
            "predicted": predicted,
            "correct": expected.strip().lower() == predicted.strip().lower(),
        })

    return results


def run_evaluation() -> None:
    ground_truth_files = sorted(GROUND_TRUTH_DIR.glob("*_ground_truth.json"))

    if not ground_truth_files:
        print("No ground truth files found in output/ground_truth")
        return

    all_results = []
    for file_path in ground_truth_files:
        all_results.extend(evaluate_document(file_path))

    total = len(all_results)
    correct = sum(1 for row in all_results if row["correct"])
    accuracy = (correct / total * 100) if total else 0.0

    print(f"Evaluated {total} question-answer pairs")
    print(f"Correct: {correct}")
    print(f"Accuracy: {accuracy:.2f}%")
    print()

    for row in all_results[:10]:
        print(
            f"{row['document_id']} | {row['question']} | "
            f"expected={row['expected']} | predicted={row['predicted']} | "
            f"correct={row['correct']}"
        )


if __name__ == "__main__":
    run_evaluation()