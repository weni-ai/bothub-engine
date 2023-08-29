from dataclasses import dataclass
from django.contrib.auth import get_user_model

from ..models import Project
from .exceptions import InvalidProjectData
from bothub.common.models import Organization
User = get_user_model

@dataclass
class ProjectCreationDTO:
    uuid: str
    name: str
    is_template: bool
    date_format: str
    timezone: str
    organization_id: int

class ProjectCreationUseCase:

    def get_or_create_user_by_email(self, email: str) -> tuple:
        return User.objects.get_or_create(email=email)

    def get_or_create_project(self, project_dto: ProjectCreationDTO, user: User) -> tuple:
        try: 
            organization = Organization.objects.get(pk=project_dto.organization_id)
        except Organization.DoesNotExist:
            raise InvalidProjectData(f"Organization {project_dto.organization_id} does not exists!")
        
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
        project, _ = self.get_or_create_project(project_dto, user)
