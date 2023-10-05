import requests
import logging

from django.conf import settings

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions

from bothub.common.models import (
    ZeroShotOptionsText,
    ZeroShotOptions,
    RepositoryZeroShot,
    Repository,
)

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

        classes = {}

        for categorie in data.get("categories"):
            option = categorie.get("option")
            classes[option] = [option]
            for synonym in categorie.get("synonyms"):
                classes[option].append(synonym)

        body = {
            "input": {
                "text": data.get("text"),
                "classes": classes
            }
        }

        headers = {
            "Content-Type": "application/json; charset: utf-8",
            "Authorization": f"Bearer {settings.ZEROSHOT_TOKEN}",
        }

        try:
            url = settings.ZEROSHOT_BASE_NLP_URL
            if len(settings.ZEROSHOT_SUFFIX) > 0:
                url += settings.ZEROSHOT_SUFFIX
            response_nlp = requests.post(
                headers=headers,
                url=url,
                json=body
            )
            return Response(status=response_nlp.status_code, data=response_nlp.json() if response_nlp.status_code == 200 else {"error": response_nlp.text})
        except Exception as error:
            logger.error(f"[ - ] Zeroshot fast predict: {error}")
            raise  error
