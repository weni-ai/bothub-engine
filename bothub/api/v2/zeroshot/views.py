import requests
import logging
import json

from django.conf import settings

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions

from bothub.common.models import (
    ZeroShotOptionsText,
    ZeroShotOptions,
    RepositoryZeroShot,
    Repository,
    ZeroshotLogs
)

from .usecases.format_prompt import FormatPrompt
from .usecases.format_classification import FormatClassification

from bothub.api.v2.zeroshot.permissions import ZeroshotTokenPermission

logger = logging.getLogger(__name__)

class ZeroShotOptionsTextAPIView(APIView):

    queryset = ZeroShotOptionsText.objects
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        data = request.data

        option = ZeroShotOptions.objects.create(key=data.get("option_key"))

        ZeroShotOptionsText.objects.create(text=data.get("option_text"), option=option)
        return Response(status=200)

    def get(self, request):
        data = []
        for option in self.queryset.all():
            data.append({"text": option.text, "option": option.option.key})
        return Response(status=200, data=data)


class ZeroShotRepositoryAPIView(APIView):

    queryset = RepositoryZeroShot.objects
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        user = request.user
        data = request.data

        repository = Repository.objects.create(
            name=data.get("name"),
            description=data.get("description"),
            slug=data.get("slug"),
            language=data.get("language"),
            type=Repository.TYPE_ZEROSHOT,
        )

        RepositoryZeroShot.objects.create(
            text=data.get("text"), user=user, repository=repository
        )
        return Response(status=200)

    def get(self, request):
        uuid = request.data.get("uuid")
        if not uuid:
            return Response(status=404)
        repo = RepositoryZeroShot.objects.get(uuid=uuid)
        data = {
            "name": repo.repository.name,
            "language": repo.repository.language,
            "created_at": repo.created_at,
        }
        return Response(status=200, data=data)


class ZeroShotFastPredictAPIView(APIView):

    authentication_classes = []
    permission_classes = [ZeroshotTokenPermission]

    def post(self, request):

        data = request.data

        prompt_formatter = FormatPrompt()
        
        data["language"] = prompt_formatter.get_language(data.get("language", "pt-br"))
        
        prompt = prompt_formatter.generate_prompt(data.get("language"), data)

        body = {
            "input": {
                "prompt": prompt,
                "sampling_params": {
                    "max_tokens": settings.ZEROSHOT_MAX_TOKENS,
                    "n": settings.ZEROSHOT_N,
                    "top_p": settings.ZEROSHOT_TOP_P,
                    "tok_k": settings.ZEROSHOT_TOK_K,
                    "temperature": settings.ZEROSHOT_TEMPERATURE,
                    "do_sample": settings.ZEROSHOT_DO_SAMPLE,
                    "stop": settings.ZEROSHOT_STOP
                }

            }
        }

        headers = {
            "Content-Type": "application/json; charset: utf-8",
            "Authorization": f"Bearer {settings.ZEROSHOT_TOKEN}",
        }
        response_nlp = None
        try:
            url = settings.ZEROSHOT_BASE_NLP_URL
            if len(settings.ZEROSHOT_SUFFIX) > 0:
                url += settings.ZEROSHOT_SUFFIX
            response_nlp = requests.post(
                headers=headers,
                url=url,
                json=body
            )

            response = {"output": {}}
            if response_nlp.status_code == 200:
                classification = response_nlp.json().get("output")
                classification_formatter = FormatClassification(classification)

                formatted_classification = classification_formatter.get_classify(language=data.get("language"), options=data.get("options"))
                
                response["output"] = formatted_classification

            ZeroshotLogs.objects.create(
                text=data.get("text"),
                classification=response["output"].get("classification"),
                other=response["output"].get("other", False),
                options=data.get("options"),
                nlp_log=str(response_nlp.json()),
                language=data.get("language")
            )

            return Response(status=response_nlp.status_code, data=response if response_nlp.status_code == 200 else {"error": response_nlp.text})
        except Exception as error:
            logger.error(f"[ - ] Zeroshot fast predict: {error}")
            return Response(status=response_nlp.status_code if response_nlp else 500, data={"error": error})
