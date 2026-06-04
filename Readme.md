# Medical Document QA with Amazon Bedrock Nova

This project extracts answers from medical documents using Amazon Bedrock and evaluates question-answer performance on a labeled dataset.

## Overview

The application uses Amazon Bedrock for question answering over medical-note context and is currently configured to work with **Amazon Nova** models. In testing, the current setup evaluated 30 question-answer pairs and achieved 30 correct answers, for 100% accuracy on the present evaluation set.[1]

The earlier Bedrock invocation issue was caused by using model parameters that did not match the selected model schema. Bedrock requires request bodies to match the target model family, and Amazon Nova uses its own request structure for inference settings.[2][3]

## Current model setup

The project is intended to run with a Nova model such as:

```env
BEDROCK_MODEL_ID=amazon.nova-micro-v1:0
```

Amazon documents that Nova models can be invoked through Bedrock using the `InvokeModel` or `Converse` APIs.[2]

## Key implementation notes

- Use a Nova-specific request body.
- Put generation settings under `inferenceConfig`.
- Use `maxTokens` for Nova rather than `max_tokens`.
- Keep Bedrock request construction in the service layer.

A typical Nova request shape looks like this:

```json
{
  "messages": [
    {
      "role": "user",
      "content": [
        { "text": "Question here" }
      ]
    }
  ],
  "inferenceConfig": {
    "maxTokens": 512,
    "temperature": 0,
    "topP": 0.9
  }
}
```

Amazon Bedrock documentation describes that inference requests must follow model-specific formats, which is why Claude-style fields cannot be reused unchanged with Nova.[3][2]

## Suggested project structure

```text
app/
├── api/
├── core/
│   └── config.py
├── services/
│   └── bedrock_service.py
├── main.py
├── .env
└── evaluation/
    └── run_bedrock_eval.py
```

The main Bedrock request and response handling logic should live in `app/services/bedrock_service.py`, while configuration such as `BEDROCK_MODEL_ID` should live in environment variables or settings management.[2]

## Running the project

1. Configure AWS credentials with access to Amazon Bedrock.
2. Set the Bedrock region and Nova model ID in `.env`.
3. Start the application.
4. Run the evaluation script against the labeled QA dataset.

If a different provider model is later enabled, request format changes may be required because Bedrock model access and request schemas vary by model family.[4][3]

## Evaluation

The current evaluation result is:

- Total question-answer pairs: 30
- Correct answers: 30
- Accuracy: 100%
- Diagnosis questions: 10/10
- Doctor questions: 10/10
- Medication questions: 10/10

Amazon Bedrock also provides native evaluation workflows for prompts, models, and knowledge-base resources, which can be useful when expanding the test set beyond the current sample.[1][5]

## Next improvements

- Expand the dataset to include negative and ambiguous cases.
- Compare Nova Micro and Nova Lite for cost versus quality.
- Add prompt versioning and structured evaluation runs.
- Add a simple API or frontend demo.

Amazon recommends using prompt datasets and evaluation workflows when measuring prompt or model performance more systematically.[5][1]