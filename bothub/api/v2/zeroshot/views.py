import requests

from django.conf import settings

from rest_framework import permissions
from rest_framework.exceptions import NotFound
from rest_framework.views import APIView
from rest_framework.response import Response

from bothub.common.models import (
    ZeroShotOptionsText,
    ZeroShotOptions,
    RepositoryZeroShot,
    Repository,
)


class ZeroShotOptionsTextAPIView(APIView):

    queryset = ZeroShotOptionsText.objects
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        data = request.data

        try:
            zeroshot = RepositoryZeroShot.objects.get(repository__uuid=data.get("repository_uuid"))
        except Exception as err:
            return Response(status=404, data={"error": f"repository not found {err}"})

        try:
            option = ZeroShotOptions.objects.get(key=data.get("option_key"), repository_zeroshot=zeroshot)
        except Exception as err:
            option = ZeroShotOptions.objects.create(key=data.get("option_key"), repository_zeroshot=zeroshot)
            print(f"[ + ] err: {err}")
        synonyms = []
        for synonym in data.get("option_text"):
            option_synonym = ZeroShotOptionsText.objects.create(text=synonym, option=option)
            synonyms.append(option_synonym.text)
        return Response(status=200, data={"option": option.key, "synonym": synonyms})

    def get(self, request):
        data = []
        current_queryset = self.queryset.filter(option__repository_zeroshot__repository__uuid=request.data.get("repository_uuid"))
        if request.data.get("option_key"):
            current_queryset = current_queryset.filter(option__key=request.data.get("option_key"))
        for option in current_queryset:
            data.append({"id": option.pk, "text": option.text, "option": option.option.key})
        return Response(status=200, data=data)

    def patch(self, request):
        option_id = request.data.get("id")
        try:
            option = ZeroShotOptionsText.objects.get(pk=option_id)
        except Exception as err:
            print(f'error: {err}')
            raise NotFound(f"Synonym {option_id} not found")
        option.text = request.data.get("text")
        option.save(update_fields=["text"])
        return Response(status=200, data={"id": option.pk, "text": option.text, "option": option.option.key})

    def delete(self, request):
        option_id = request.data.get("id")
        try:
            option = ZeroShotOptionsText.objects.get(pk=option_id)
        except Exception as err:
            print(f"error: {err}")
            raise NotFound(f"Synonym {option_id} not found")
        option.delete()
        return Response(status=200, data={"message": f"Synonym {option_id} has been deleted!"})


class ZeroShotOptionsAPIView(APIView):
    queryset = ZeroShotOptions.objects
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        data = request.data
        zeroshot = None
        try:
            zeroshot = RepositoryZeroShot.objects.get(repository__uuid=data.get("repository_uuid"))
        except Exception as err:
            return Response(status=404, data={"error": f"repository not found {err}"})

        option = ZeroShotOptions.objects.create(key=data.get("option_key"), repository_zeroshot=zeroshot)
        return Response(status=200, data={"id": option.pk, "key": option.key})

    def get(self, request):
        data = request.data
        zeroshot = None
        try:
            zeroshot = RepositoryZeroShot.objects.get(repository__uuid=data.get("repository_uuid"))
        except Exception as err:
            return Response(status=404, data={"error": f"repository not found {err}"})
        options = []
        for option in self.queryset.filter(repository_zeroshot=zeroshot):
            options.append({"id": option.pk, "key": option.key})
        return Response(status=200, data=options)

    def patch(self, request):
        data = request.data
        zeroshot = None
        try:
            zeroshot = RepositoryZeroShot.objects.get(repository__uuid=data.get("repository_uuid"))
        except Exception as err:
            return Response(status=404, data={"error": f"repository not found {err}"})
        option = None
        try:
            option = ZeroShotOptions.objects.get(key=data.get("option_key"), repository_zeroshot=zeroshot)
        except Exception as err:
            print(f"error: {err}")
            raise NotFound("Intent not found")
        option.key = data.get("option_key")
        option.save(update_fields=["key"])
        return Response(status=200, data={"id": option.pk, "key": option.key})

    def delete(self, request):
        data = request.data
        zeroshot = None
        try:
            zeroshot = RepositoryZeroShot.objects.get(repository__uuid=data.get("repository_uuid"))
        except Exception as err:
            return Response(status=404, data={"error": f"repository not found {err}"})
        option = None
        try:
            option = ZeroShotOptions.objects.get(key=data.get("option_key"), repository_zeroshot=zeroshot)
        except Exception as err:
            print(f"[ + ] error: {err}")
            raise NotFound("Intent not found")
        option.delete()
        return Response(status=200, data={"message": f"Intent {data.get('option_key')} has been deleted!"})


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


class ZeroShotPredictAPIView(APIView):

    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        user = request.user
        data = request.data

        repository = Repository.objects.get(uuid=data.get("uuid"))
        auth = repository.get_user_authorization(user)

        if auth is None:
            return Response(status=400, data={"message": "you don't have permission"})

        zero_shot_repository = RepositoryZeroShot.objects.get(repository=repository)

        options = ZeroShotOptionsText.objects.filter(option__repository_zeroshot=zero_shot_repository)
        options_body = {}
        for option_text in options:
            if option_text.option.key in options_body:
                options_body[option_text.option.key] = []
            options_body[option_text.option.key].append(option_text.text)

        body = {
            "text": data.get("text"),
            "classes": options_body
        }

        response_nlp = requests.post(
            url=f"{settings.ZEROSHOT_BASE_NLP_URL}/zshot",
            body=body
        )

        return Response(status=response_nlp.status_code, data=response_nlp.json() if response_nlp.status_code == 200 else {"error": response_nlp.text})


class ZeroShotFastPredictAPIView(APIView):

    def post(self, request):
        data = request.data

        auth = data.get("token")

        if auth is not settings.FLOWS_TOKEN_ZEROSHOT:
            return Response(status=401, data={"error": "You don't have permission to do this."})

        classes = {}

        for categorie in data.get("categories"):
            option = categorie.get("option")
            classes[option] = []
            for synonym in categorie.get("synonyms"):
                classes[option].append(synonym)

        body = {
            "text": data.get("text"),
            "classes": classes
        }
        try:
            response_nlp = requests.post(
                url=f"{settings.ZEROSHOT_BASE_NLP_URL}/zshot",
                json=body
            )
        except Exception as error:
            print(f'error: {error}')
        return Response(status=response_nlp.status_code, data=response_nlp.json() if response_nlp.status_code == 200 else {"error": response_nlp.text})
