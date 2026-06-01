import json
from pathlib import Path
from app.core.config import get_settings
from app.services.bedrock_service import BedrockService


GROUND_TRUTH_DIR = Path("output/ground_truth")
EXTRACTED_DIR = Path("data/extracted")

QUESTIONS = {
    "What is the diagnosis?": "diagnosis",
    "Who is the doctor?": "doctor",
    "What medication was prescribed?": "medication",
}


def load_json(file_path: Path) -> dict:
    return json.loads(file_path.read_text(encoding="utf-8"))


def normalize_text(value: str) -> str:
    return " ".join(value.strip().lower().split())


def evaluate_document(ground_truth_file: Path, bedrock_service: BedrockService) -> list[dict]:
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

    context = extracted_file.read_text(encoding="utf-8").strip()
    if not context:
        return [{
            "document_id": document_id,
            "question": "ALL",
            "expected": "N/A",
            "predicted": "Empty extracted file",
            "correct": False,
        }]

    expected_fields = gt.get("expected_fields", {})
    results = []

    for question, field_name in QUESTIONS.items():
        expected = expected_fields.get(field_name, "N/A")

        try:
            predicted = bedrock_service.ask_question(
                context=context,
                question=question,
            )
        except Exception as e:
            predicted = f"ERROR: {str(e)}"

        results.append({
            "document_id": document_id,
            "question": question,
            "expected": expected,
            "predicted": predicted,
            "correct": normalize_text(expected) == normalize_text(predicted),
        })

    return results


def summarize_results(all_results: list[dict]) -> None:
    total = len(all_results)
    correct = sum(1 for row in all_results if row["correct"])
    accuracy = (correct / total * 100) if total else 0.0

    print(f"Evaluated {total} question-answer pairs")
    print(f"Correct: {correct}")
    print(f"Accuracy: {accuracy:.2f}%")
    print()

    question_buckets = {}
    for row in all_results:
        question = row["question"]
        question_buckets.setdefault(question, []).append(row)

    for question, rows in question_buckets.items():
        q_total = len(rows)
        q_correct = sum(1 for row in rows if row["correct"])
        q_accuracy = (q_correct / q_total * 100) if q_total else 0.0
        print(f"{question} -> {q_correct}/{q_total} correct ({q_accuracy:.2f}%)")

    print()
    for row in all_results[:15]:
        print(
            f"{row['document_id']} | {row['question']} | "
            f"expected={row['expected']} | predicted={row['predicted']} | "
            f"correct={row['correct']}"
        )


def run_bedrock_evaluation() -> None:
    ground_truth_files = sorted(GROUND_TRUTH_DIR.glob("*_ground_truth.json"))

    if not ground_truth_files:
        print("No ground truth files found in output/ground_truth")
        return

    from app.core.config import get_settings


    settings = get_settings()
    bedrock_service = BedrockService(model_id=settings.BEDROCK_MODEL_ID)
    all_results = []

    for file_path in ground_truth_files:
        all_results.extend(evaluate_document(file_path, bedrock_service))

    summarize_results(all_results)


if __name__ == "__main__":
    run_bedrock_evaluation()