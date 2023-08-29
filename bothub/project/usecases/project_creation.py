from dataclasses import dataclass
from django.contrib.auth import get_user_model

from ..models import Project

User = get_user_model

@dataclass
class ProjectCreationDTO:
    uuid: str
    name: str
    is_template: bool
    date_format: str
    timezone: str

class ProjectCreationUseCase:

    def get_or_create_user_by_email(self, email: str) -> tuple:
        return User.objects.get_or_create(email=email)

    def get_or_create_project(self, project_dto: ProjectCreationDTO, user: User) -> tuple:
        return Project.objects.get_or_create(
            uuid=project_dto.uuid,
            defaults=dict(
                name=project_dto.name,
                date_format=project_dto.date_format,
                timezone=project_dto.timezone,
                created_by=user,
                is_template=project_dto.is_template,
            ),
        )

    def create_project(self, project_dto: ProjectCreationDTO, user_email: str) -> None:
        user, _ = self.get_or_create_user_by_email(user_email)
        project, _ = self.get_or_create_project(project_dto, user)

        if project_dto.is_template:
            self.__template_type_integration.integrate_template_type_in_project(
                project, project_dto.template_type_uuid, user
            )