import time
from pathlib import Path

import boto3
from botocore.exceptions import ClientError

from app.core.config import get_settings


class TextractService:
    def __init__(self):
        self.settings = get_settings()
        self.client = boto3.client(
            "textract",
            region_name=self.settings.AWS_REGION,
        )

    def extract_text_from_file(self, file_path: Path) -> str:
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        document_bytes = file_path.read_bytes()

        try:
            response = self.client.analyze_document(
                Document={"Bytes": document_bytes},
                FeatureTypes=self.settings.TEXTRACT_FEATURES,
            )
        except ClientError as e:
            raise RuntimeError(f"Textract sync extraction failed: {str(e)}") from e

        return self._extract_lines_from_blocks(response.get("Blocks", []))

    def start_document_analysis(self, s3_bucket: str, s3_key: str) -> str:
        try:
            response = self.client.start_document_analysis(
                DocumentLocation={
                    "S3Object": {
                        "Bucket": s3_bucket,
                        "Name": s3_key,
                    }
                },
                FeatureTypes=self.settings.TEXTRACT_FEATURES,
            )
        except ClientError as e:
            raise RuntimeError(f"Textract async start failed: {str(e)}") from e

        return response["JobId"]

    def get_document_analysis(self, job_id: str, max_results: int = 1000) -> dict:
        all_blocks = []
        next_token = None
        document_metadata = None
        job_status = None

        while True:
            kwargs = {
                "JobId": job_id,
                "MaxResults": max_results,
            }
            if next_token:
                kwargs["NextToken"] = next_token

            try:
                response = self.client.get_document_analysis(**kwargs)
            except ClientError as e:
                raise RuntimeError(f"Textract async fetch failed: {str(e)}") from e

            job_status = response.get("JobStatus")
            document_metadata = response.get("DocumentMetadata", document_metadata)

            all_blocks.extend(response.get("Blocks", []))
            next_token = response.get("NextToken")

            if not next_token:
                break

        return {
            "JobStatus": job_status,
            "DocumentMetadata": document_metadata,
            "Blocks": all_blocks,
        }

    def wait_for_analysis(self, job_id: str, poll_seconds: int = 3, timeout_seconds: int = 300) -> dict:
        start_time = time.time()

        while True:
            if time.time() - start_time > timeout_seconds:
                raise TimeoutError(f"Textract job timed out after {timeout_seconds} seconds")

            try:
                response = self.client.get_document_analysis(JobId=job_id, MaxResults=1000)
            except ClientError as e:
                raise RuntimeError(f"Textract polling failed: {str(e)}") from e

            status = response.get("JobStatus")

            if status == "SUCCEEDED":
                return self.get_document_analysis(job_id=job_id)

            if status in {"FAILED", "PARTIAL_SUCCESS"}:
                raise RuntimeError(f"Textract job ended with status: {status}")

            time.sleep(poll_seconds)

    def extract_text_from_s3_pdf(self, s3_bucket: str, s3_key: str) -> str:
        job_id = self.start_document_analysis(s3_bucket=s3_bucket, s3_key=s3_key)
        result = self.wait_for_analysis(job_id=job_id)
        return self._extract_lines_from_blocks(result.get("Blocks", []))

    def _extract_lines_from_blocks(self, blocks: list[dict]) -> str:
        lines = []

        for block in blocks:
            if block.get("BlockType") == "LINE":
                text = block.get("Text", "").strip()
                if text:
                    lines.append(text)

        return "\n".join(lines)