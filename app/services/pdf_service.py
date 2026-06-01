from pathlib import Path


class PDFService:
    def ensure_supported_file(self, file_path: Path) -> None:
        allowed_suffixes = {".pdf", ".png", ".jpg", ".jpeg"}
        if file_path.suffix.lower() not in allowed_suffixes:
            raise ValueError(f"Unsupported file type: {file_path.suffix}")