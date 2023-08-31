import uuid

from django.contrib.auth import get_user_model

from bothub.common.models import Repository
from bothub.project.models import Project, ProjectIntelligence, TemplateType
from bothub.project.usecases.interfaces import TemplateTypeIntegrationInterface
from bothub.project.usecases.exceptions import InvalidTemplateTypeData

User = get_user_model()


class TemplateTypeIntegrationUseCase(TemplateTypeIntegrationInterface):

    def integrate_template_type_in_project(self, project: "Project", template_type_uuid: str, user: "User"):

        if project.template_type is not None:
            raise InvalidTemplateTypeData(f"The project `{project.uuid}` already has an integrated template!")

        if template_type_uuid is None:
            raise InvalidTemplateTypeData("'template_type_uuid' cannot be empty when 'is_template' is True!")

        try:
            template_type = TemplateType.objects.get(uuid=template_type_uuid)
        except TemplateType.DoesNotExist:
            raise InvalidTemplateTypeData(f"Template Type with uuid `{template_type_uuid}` does not exists!")

        for repository_uuid in template_type.setup["repositories"]:
            repository = Repository.objects.get(uuid=repository_uuid)

            organization_authorization = project.organization.get_organization_authorization(user)

            if not organization_authorization.can_contribute:
                raise InvalidTemplateTypeData("The user dont have permission on that organization")

            access_token = str(
                repository.get_user_authorization(
                    organization_authorization.organization
                ).uuid
            )

            ProjectIntelligence.objects.create(
                uuid=uuid.uuid4(),
                access_token=access_token,
                integrated_by=user,
                project=project,
                name=repository.name,
                repository=repository,
            )
