from django.contrib.auth import get_user_model

from rest_framework.exceptions import NotFound
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework import permissions

from bothub.api.v2.internal.permissions import ModuleHasPermission
from bothub.common.models import Organization
from bothub.project.models import Project
from bothub.project.serializers import ProjectSerializer


User = get_user_model()


class ProjectAPIView(APIView):

    permission_classes = [ModuleHasPermission]

    def post(self, request):
        data = request.data

        if Project.objects.filter(uuid=data.get("project_uuid")).exists():
            return Response(data={"message": "That project already exists"}, status=status.HTTP_400_BAD_REQUEST)
        if not Organization.objects.filter(pk=data.get("intelligence_organization")).exists():
            return Response(data={"message": "Organization not found"}, status=status.HTTP_404_NOT_FOUND)
        if not User.objects.filter(email=data.get("created_by")).exists():
            return Response(data={"message": f"User {data.get('created_by')} not found"}, status=status.HTTP_404_NOT_FOUND)
        created_by = User.objects.get(email=data.get("created_by"))
        organization = Organization.objects.get(pk=data.get("intelligence_organization"))
        project = Project.objects.create(
            created_by=created_by,
            date_format=data.get("date_format"),
            is_template=data.get("is_template"),
            timezone=data.get("timezone"),
            name=data.get("name"),
            organization=organization,
            uuid=data.get("project_uuid")
        )
        project_serializer = ProjectSerializer(project)
        return Response(status=status.HTTP_200_OK, data=project_serializer.data)

    def get(self, request):
        self.permission_classes = [permissions.IsAuthenticated]
        data = request.data

        try:
            project = Project.objects.get(uuid=data("project_uuid"), is_active=True)
        except Exception:
            raise NotFound("Project not found!")

        project_serializer = ProjectSerializer(project)
        return Response(status=status.HTTP_200_OK, data=project_serializer.data)

    def patch(self, request):
        data = request.data

        try:
            project = Project.objects.get(uuid=data("project_uuid"), is_active=True)
        except Exception:
            raise NotFound("Project not found")
        updated_fields = []

        if "name" in data:
            updated_fields.append("name")
            project.name = data.get("name")

        if "timezone" in data:
            updated_fields.append("timezone")
            project.timezone = data.get("timezone")

        if "date_format" in data:
            updated_fields.append("date_format")
            project.date_fomat = data.get("date_format")
        project.save(update_fields=updated_fields)
        project_serializer = ProjectSerializer(project)
        return Response(status=status.HTTP_200_OK, data=project_serializer.data)

    def delete(self, request):
        data = request.data

        try:
            project = Project.objects.get(uuid=data.get("project_uuid"), is_active=True)
        except Exception:
            raise NotFound("Project not found")

        project.is_active = False
        project.save(update_fields=["is_active"])
