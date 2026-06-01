import json
from pathlib import Path

JSON_DIR = Path("output/json")
EXTRACTED_DIR = Path("data/extracted")
EXTRACTED_DIR.mkdir(parents=True, exist_ok=True)


def build_text(doc: dict) -> str:
    lines = [
        f"Document ID: {doc['document_id']}",
        f"Patient Name: {doc['patient_name']}",
        f"Test Name: {doc['test_name']}",
        f"Diagnosis: {doc['diagnosis']}",
        f"Medication: {doc['medication']}",
        f"Doctor: {doc['doctor']}",
        f"Encounter ID: {doc['encounter_id']}",
        "",
        "Narrative:",
        doc["narrative"],
        "",
        "Lab Values:",
    ]

    for key, value in doc.get("lab_values", {}).items():
        lines.append(f"{key}: {value}")

    return "\n".join(lines)


def main():
    json_files = sorted(JSON_DIR.glob("*.json"))

    if not json_files:
        print("No JSON files found in output/json")
        return

    for file_path in json_files:
        doc = json.loads(file_path.read_text(encoding="utf-8"))
        output_path = EXTRACTED_DIR / f"{doc['document_id']}.txt"
        output_path.write_text(build_text(doc), encoding="utf-8")

    print(f"Created {len(json_files)} extracted text files in {EXTRACTED_DIR}")


if __name__ == "__main__":
    main()
    