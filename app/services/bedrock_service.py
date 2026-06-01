import json
import boto3

class BedrockService:
    def __init__(self, model_id: str, region_name: str = "us-east-1"):
        self.model_id = "amazon.nova-micro-v1:0"
        self.client = boto3.client("bedrock-runtime", region_name=region_name)

    def ask_question(self, context: str, question: str) -> str:
        prompt = (
            "Answer using only the provided document context. "
            "If the answer is not explicitly present, reply exactly: Not found in document.\n\n"
            f"Document context:\n{context[:12000]}\n\n"
            f"Question: {question}"
        )

        if self.model_id.startswith("anthropic."):
            body = {
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": 512,
                "temperature": 0,
                "messages": [
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            }
        elif self.model_id.startswith("amazon.nova"):
            body = {
                "messages": [
                    {
                        "role": "user",
                        "content": [
                            {"text": prompt}
                        ]
                    }
                ],
                "inferenceConfig": {
                    "maxTokens": 512,
                    "temperature": 0,
                    "topP": 0.9
                }
            }
        else:
            raise ValueError(f"Unsupported model format for model_id={self.model_id}")

        response = self.client.invoke_model(
            modelId=self.model_id,
            body=json.dumps(body),
            contentType="application/json",
            accept="application/json",
        )

        response_body = json.loads(response["body"].read())

        if self.model_id.startswith("anthropic."):
            return response_body["content"][0]["text"].strip()
        elif self.model_id.startswith("amazon.nova"):
            return response_body["output"]["message"]["content"][0]["text"].strip()

        return "Not found in document"