from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import authentication, permissions
from django.contrib.auth.models import User

from bothub.common.models import (
    ZeroShotOptionsText,
    ZeroShotOptions,
    RepositoryZeroShot,
    Repository
)


class ZeroShotOptionsTextAPIView(APIView):

    queryset = ZeroShotOptionsText.objects
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        data = request.data

        option = ZeroShotOptions.objects.create(
            key=data.get("option_key")
        )

        ZeroShotOptionsText.objects.create(
            text=data.get("option_text"),
            option=option
        )
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
            type=Repository.TYPE_ZEROSHOT
        )

        RepositoryZeroShot.objects.create(
            text=data.get("text"),
            user = user,
            repository= repository
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
            "created_at": repo.created_at
        }
        return Response(status=200, data=data)