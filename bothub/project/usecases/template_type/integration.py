import uuid

from django.contrib.auth import get_user_model

from bothub.common.models import Repository
from bothub.project.models import Project, TemplateType, ProjectIntelligence
from bothub.project.usecases.exceptions import InvalidTemplateTypeData

User = get_user_model()


class TemplateTypeIntegrationUseCase:

    def integrate_template_type_in_project(self, project: Project, template_type_uuid: str, user: User) -> bool:
        if project.template_type is not None:
            raise InvalidTemplateTypeData(f"The project `{project.uuid}` already has an integrated template!")

        if template_type_uuid is None:
            raise InvalidTemplateTypeData("'template_type_uuid' cannot be empty when 'is_template' is True!")

        try:
            template_type = TemplateType.objects.get(uuid=template_type_uuid)
        except TemplateType.DoesNotExist:
            raise InvalidTemplateTypeData(f"Template Type with uuid `{template_type_uuid}` does not exists!")

        for repository_data in template_type.setup["repositories"]:
            repository_uuid = repository_data.get("uuid")

            repository = Repository.objects.get(uuid=repository_uuid)

            organization_authorization = project.organization.get_organization_authorization(user)        

            if not organization_authorization.can_contribute:
                raise InvalidTemplateTypeData("The user dont have permission on that organization")

            access_token = str(repository.get_user_authorization(
                    organization_authorization.organization
                ).uuid
            )

            project_intelligence = ProjectIntelligence.objects.create(
                uuid=uuid.uuid4(),
                access_token=access_token,
                integrated_by=user,
                project=project,
                name=repository.name,
                repository=repository,
            )
            print(f"[ TemplateTypeIntegration ] - adding integration to `{project.uuid}` with access token `{project_intelligence.access_token}` and uuid `{project_intelligence.uuid}`")
