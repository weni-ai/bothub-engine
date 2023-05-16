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
            RepositoryZeroShot.objects.get(repository__uuid=data.get("repository_uuid"))
            option = ZeroShotOptions.objects.create(key=data.get("option_key"))
            ZeroShotOptionsText.objects.create(text=data.get("option_text"), option=option)
        except:
            return Response(status=404, data={"error": "repository not found"})
        return Response(status=200)

    def get(self, request):
        data = []
        for option in self.queryset.filter(repository_options__uuid=request.data.get("repository_uuid")):
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
