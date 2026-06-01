import json
import random
from pathlib import Path
from uuid import uuid4
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas


OUTPUT_ROOT = Path("output")
JSON_DIR = OUTPUT_ROOT / "json"
GROUND_TRUTH_DIR = OUTPUT_ROOT / "ground_truth"
HTML_DIR = OUTPUT_ROOT / "html"
PDF_DIR = OUTPUT_ROOT / "pdf"


PATIENT_NAMES = [
    "Aarav Sharma",
    "Priya Nair",
    "Rohan Verma",
    "Sneha Iyer",
    "Karan Mehta",
]

TEST_NAMES = [
    "Complete Blood Count",
    "Liver Function Test",
    "Renal Function Panel",
    "Lipid Profile",
    "Thyroid Profile",
]

DIAGNOSES = [
    "Iron deficiency anemia",
    "Viral fever",
    "Type 2 diabetes mellitus",
    "Community acquired pneumonia",
    "Mild hypothyroidism",
]

MEDICATIONS = [
    "Paracetamol 650 mg",
    "Metformin 500 mg",
    "Azithromycin 500 mg",
    "Levothyroxine 50 mcg",
    "Ferrous sulfate 325 mg",
]

DOCTORS = [
    "Dr. Ananya Rao",
    "Dr. Vikram Sen",
    "Dr. Neha Kapoor",
    "Dr. Rahul Menon",
]


def ensure_directories() -> None:
    for path in [JSON_DIR, GROUND_TRUTH_DIR, HTML_DIR, PDF_DIR]:
        path.mkdir(parents=True, exist_ok=True)


def generate_document(doc_index: int) -> dict:
    patient_name = random.choice(PATIENT_NAMES)
    test_name = random.choice(TEST_NAMES)
    diagnosis = random.choice(DIAGNOSES)
    medication = random.choice(MEDICATIONS)
    doctor = random.choice(DOCTORS)

    document_id = f"DOC-{doc_index:04d}"
    encounter_id = str(uuid4())[:8].upper()

    values = {
        "hemoglobin_g_dl": round(random.uniform(8.5, 15.8), 1),
        "wbc_count": random.randint(3500, 14000),
        "platelet_count": random.randint(120000, 450000),
        "glucose_mg_dl": random.randint(70, 220),
    }

    narrative = (
        f"Patient {patient_name} visited the clinic for evaluation. "
        f"The ordered test was {test_name}. "
        f"The working diagnosis was {diagnosis}. "
        f"Prescribed medication: {medication}. "
        f"Consulting physician: {doctor}. "
        f"Encounter ID: {encounter_id}."
    )

    return {
        "document_id": document_id,
        "document_type": "synthetic_medical_record",
        "patient_name": patient_name,
        "test_name": test_name,
        "diagnosis": diagnosis,
        "medication": medication,
        "doctor": doctor,
        "encounter_id": encounter_id,
        "lab_values": values,
        "narrative": narrative,
    }


def save_json(document: dict) -> None:
    output_file = JSON_DIR / f"{document['document_id']}.json"
    with output_file.open("w", encoding="utf-8") as f:
        json.dump(document, f, indent=2, ensure_ascii=False)


def save_ground_truth(document: dict) -> None:
    ground_truth = {
        "document_id": document["document_id"],
        "expected_fields": {
            "patient_name": document["patient_name"],
            "test_name": document["test_name"],
            "diagnosis": document["diagnosis"],
            "medication": document["medication"],
            "doctor": document["doctor"],
            "encounter_id": document["encounter_id"],
        },
        "expected_answer_examples": {
            "What is the diagnosis?": document["diagnosis"],
            "Who is the doctor?": document["doctor"],
            "What medication was prescribed?": document["medication"],
        },
    }

    output_file = GROUND_TRUTH_DIR / f"{document['document_id']}_ground_truth.json"
    with output_file.open("w", encoding="utf-8") as f:
        json.dump(ground_truth, f, indent=2, ensure_ascii=False)


def save_html_placeholder(document: dict) -> None:
    html = f"""
    <html>
      <head>
        <title>{document['document_id']}</title>
      </head>
      <body>
        <h1>Synthetic Medical Document</h1>
        <p><strong>Document ID:</strong> {document['document_id']}</p>
        <p><strong>Patient:</strong> {document['patient_name']}</p>
        <p><strong>Test:</strong> {document['test_name']}</p>
        <p><strong>Diagnosis:</strong> {document['diagnosis']}</p>
        <p><strong>Medication:</strong> {document['medication']}</p>
        <p><strong>Doctor:</strong> {document['doctor']}</p>
        <p><strong>Narrative:</strong> {document['narrative']}</p>
      </body>
    </html>
    """.strip()

    output_file = HTML_DIR / f"{document['document_id']}.html"
    output_file.write_text(html, encoding="utf-8")


def save_pdf(document: dict) -> None:
    output_file = PDF_DIR / f"{document['document_id']}.pdf"
    c = canvas.Canvas(str(output_file), pagesize=A4)

    y = 800
    line_gap = 22

    c.setTitle(document["document_id"])
    c.setFont("Helvetica-Bold", 16)
    c.drawString(50, y, "Synthetic Medical Document")
    y -= 2 * line_gap

    c.setFont("Helvetica", 11)
    lines = [
        f"Document ID: {document['document_id']}",
        f"Patient Name: {document['patient_name']}",
        f"Test Name: {document['test_name']}",
        f"Diagnosis: {document['diagnosis']}",
        f"Medication: {document['medication']}",
        f"Doctor: {document['doctor']}",
        f"Encounter ID: {document['encounter_id']}",
        "",
        "Narrative:",
        document["narrative"],
        "",
        "Lab Values:",
    ]

    for line in lines:
        c.drawString(50, y, line)
        y -= line_gap

    for key, value in document["lab_values"].items():
        c.drawString(70, y, f"{key}: {value}")
        y -= line_gap

    c.save()

def run_dataset(num_documents: int = 10) -> None:
    ensure_directories()

    for i in range(1, num_documents + 1):
        document = generate_document(i)
        save_json(document)
        save_ground_truth(document)
        save_html_placeholder(document)
        save_pdf(document)

    print(f"Generated {num_documents} synthetic documents in {OUTPUT_ROOT}")


if __name__ == "__main__":
    run_dataset()