from django.utils import translation


class UserLanguageMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        user = getattr(request, "user", None)
        if not user or user.is_anonymous:
            return self.get_response(request)

        user_language = getattr(user, "language", None)
        if not user_language:
            return self.get_response(request)

        translation.activate(user_language)

        response = self.get_response(request)

        return response


class ProjectOrganizationMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, project_uuid, *args, **kwargs):
        from bothub.common.models import Project
        from bothub.api.v2.internal.connect_rest_client import ConnectRESTClient
        from bothub.utils import organization_unique_slug_generator
        project_uuid = kwargs.get("project_uuid")
        project = Project.objects.filter(uuid=project_uuid)
        
        if project.exists():
            project = project.first()
            return project

        connect_client = ConnectRESTClient()
        response = connect_client.get_project_info(project_uuid=project_uuid)
        if response.status_code == 200:
            project_data = response.get("project")
            is_template = project_data.get("is_template", False)
            if not is_template:
                organization_data = response.get("organization")
                authorizations = response.get("authorizations")
                owner = response.get("owner")

                formatted_organization_data = {
                    "name": organization_data.get("name"),
                    "nickname": organization_unique_slug_generator(
                        organization_data.get("name")
                    ),
                    "description": organization_data.get("description", ""),
                    "locale": organization_data.get("locale", ""),
                }
                org = Organization.objects.create(**formatted_organization_data)

                Project.objects.create(
                    uuid=project_data.get("uuid"),
                    name=project_data.get("name"),
                    organization=org
                )