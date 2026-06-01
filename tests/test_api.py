from pathlib import Path

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["message"] == "API is running"


def test_health():
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_upload_document():
    file_content = b"fake image content"
    files = {
        "file": ("test.png", file_content, "image/png")
    }

    response = client.post("/api/v1/documents/upload", files=files)

    assert response.status_code == 201
    body = response.json()
    assert body["status"] == "uploaded"
    assert body["content_type"] == "image/png"
    assert "document_id" in body
    assert "stored_filename" in body


def test_query_document_with_mock(monkeypatch):
    extracted_dir = Path("data/extracted")
    extracted_dir.mkdir(parents=True, exist_ok=True)

    document_id = "TEST-QUERY-0001"
    extracted_file = extracted_dir / f"{document_id}.txt"
    extracted_file.write_text(
        "Patient diagnosis: Viral fever. Prescribed medication: Paracetamol 650 mg.",
        encoding="utf-8",
    )

    from app.api.v1.endpoints import query as query_module

    def mock_ask_question(context: str, question: str) -> str:
        return "Viral fever"

    monkeypatch.setattr(query_module.bedrock_service, "ask_question", mock_ask_question)

    response = client.post(
        f"/api/v1/documents/{document_id}/query",
        json={
            "question": "What is the diagnosis?",
            "include_context_preview": True
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["document_id"] == document_id
    assert body["answer"] == "Viral fever"
    assert body["status"] == "answered"
    assert body["context_chars"] > 0
    assert body["context_preview"] is not None


def test_query_document_not_found():
    response = client.post(
        "/api/v1/documents/DOES-NOT-EXIST/query",
        json={"question": "What is the diagnosis?"},
    )

    assert response.status_code == 404
    assert "Extracted text not found" in response.json()["detail"]