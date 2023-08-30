from django.contrib.auth import get_user_model

from .projectdto import ProjectCreationDTO

from bothub.common.models import Organization
from bothub.project.usecases.exceptions import InvalidProjectData
from bothub.project.usecases.template_type.integration import TemplateTypeIntegrationUseCase

from bothub.project.models import Project

User = get_user_model()

class ProjectCreationUseCase:

    def get_or_create_user_by_email(self, email: str) -> tuple:
        return User.objects.get_or_create(email=email)

    def get_organization_by_id(self, organization_id):
        try: 
            return Organization.objects.get(pk=organization_id)
        except Organization.DoesNotExist:
            raise InvalidProjectData(f"Organization {organization_id} does not exists!")

    def get_or_create_project(self, project_dto: ProjectCreationDTO, user: User, organization: Organization) -> tuple:

        return Project.objects.get_or_create(
            uuid=project_dto.uuid,
            defaults=dict(      
                name=project_dto.name,
                date_format=project_dto.date_format,
                timezone=project_dto.timezone,
                created_by=user,
                is_template=project_dto.is_template,
                organization=organization
            )
        )

    def create_project(self, project_dto: ProjectCreationDTO, user_email: str) -> None:
        user, _ = self.get_or_create_user_by_email(user_email)
        organization = self.get_organization_by_id(project_dto.organization_id)
        project, _ = self.get_or_create_project(project_dto, user, organization)
        
        if project.is_template:
            template_type = TemplateTypeIntegrationUseCase()
            template_type.integrate_template_type_in_project(project=project, template_type_uuid=project_dto.template_type_uuid, user=user)