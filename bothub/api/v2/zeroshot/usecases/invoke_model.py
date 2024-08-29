import json
import requests
import boto3

from django.conf import settings
from .format_classification import FormatClassification
from .format_prompt import FormatPrompt


class InvokeModel:

    def __init__(self, zeroshot_data):
        self.model_backend = settings.ZEROSHOT_MODEL_BACKEND
        self.zeroshot_data = zeroshot_data

    def invoke(self):
        prompt = self._get_prompt(self.zeroshot_data)

        if self.model_backend == "runpod":
            return self._invoke_runpod(prompt)
        elif self.model_backend == "bedrock":
            return self._invoke_bedrock(prompt)
        else:
            raise ValueError(f"Unsupported model backend: {self.model_backend}")

    def _get_prompt(self, zeroshot_data):
        prompt_formatter = FormatPrompt()

        language = zeroshot_data.get("language", prompt_formatter.get_default_language())
        return prompt_formatter.generate_prompt(language, zeroshot_data)

    def _invoke_runpod(self, prompt):
        payload = json.dumps({
            "input": {
                "prompt": prompt,
                "sampling_params": {
                    "max_tokens": settings.ZEROSHOT_MAX_TOKENS,
                    "n": settings.ZEROSHOT_N,
                    "top_p": settings.ZEROSHOT_TOP_P,
                    "top_k": settings.ZEROSHOT_TOP_K,
                    "temperature": settings.ZEROSHOT_TEMPERATURE,
                    "stop": settings.ZEROSHOT_STOP
                }

            }
        })

        headers = {
            "Content-Type": "application/json; charset: utf-8",
            "Authorization": f"Bearer {settings.ZEROSHOT_TOKEN}",
        }
        response_nlp = None
        response = {"output": {}}
        
        url = settings.ZEROSHOT_BASE_NLP_URL
        if len(settings.ZEROSHOT_SUFFIX) > 0:
            url += settings.ZEROSHOT_SUFFIX
        response_nlp = requests.post(
            headers=headers,
            url=url,
            data=payload
        )

        if response_nlp.status_code == 200:
            classification = response_nlp.json()
            classification_formatter = FormatClassification(classification)
            formatted_classification = classification_formatter.get_classification(self.zeroshot_data)
            
            response["output"] = formatted_classification
        
        return response

    def _invoke_bedrock(self, prompt):
        response = {"output": {}}
        
        session = boto3.Session(
            aws_access_key_id=settings.ZEROSHOT_BEDROCK_AWS_KEY,
            aws_secret_access_key=settings.ZEROSHOT_BEDROCK_AWS_SECRET,
            region_name=settings.ZEROSHOT_BEDROCK_AWS_REGION
        )

        bedrock_runtime = session.client('bedrock-runtime')
        payload = json.dumps({
            "max_tokens": settings.ZEROSHOT_MAX_TOKENS,
            "top_p": settings.ZEROSHOT_TOP_P,
            "top_k": settings.ZEROSHOT_TOP_K,
            "stop": settings.ZEROSHOT_STOP,
            "temperature": settings.ZEROSHOT_TEMPERATURE,
            "prompt": prompt
        })

        response = bedrock.invoke_model(
            body=payload,
            contentType='application/json',
            accept='application/json',
            modelId=settings.ZEROSHOT_BEDROCK_MODEL_ID,
            trace='ENABLED'
        )

        classification = json.loads(response['body'].read().decode('utf-8'))

        classification_formatter = FormatClassification(classification)
        formatted_classification = classification_formatter.get_classification(self.zeroshot_data)

        response["output"] = formatted_classification
        return response


