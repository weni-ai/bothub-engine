from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions

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
        except:
            return Response(status=404, data={"error": "repository not found"})
        
        try:
            option = ZeroShotOptions.objects.get(key=data.get("option_key"), repository_zeroshot=zeroshot)
        except:
            option = ZeroShotOptions.objects.create(key=data.get("option_key"), repository_zeroshot=zeroshot)
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
            data.append({"text": option.text, "option": option.option.key})
        return Response(status=200, data=data)


class ZeroShotOptionsAPIView(APIView):
    queryset = ZeroShotOptions.objects
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        data = request.data
        zeroshot = None
        try:
            zeroshot = RepositoryZeroShot.objects.get(repository__uuid=data.get("repository_uuid"))
        except:
            return Response(status=404, data={"error": "repository not found"})

        option = ZeroShotOptions.objects.create(key=data.get("option_key"), repository_zeroshot=zeroshot)
        return Response(status=200, data={"key": option.key})
    
    def get(self, request):
        data = request.data
        zeroshot = None
        try:
            zeroshot = RepositoryZeroShot.objects.get(repository__uuid=data.get("repository_uuid"))
        except:
            return Response(status=404, data={"error": "repository not found"})
        options = []
        for option in self.queryset.filter(repository_zeroshot=zeroshot):
            options.append({"key": option.key})
        return Response(status=200, data=options)


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
