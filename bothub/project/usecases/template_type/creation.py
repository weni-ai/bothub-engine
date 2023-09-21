from .template_type_dto import TemplateTypeDTO
from bothub.project.models import ProjectIntelligence, TemplateType, Project
from bothub.project.usecases.exceptions import InvalidTemplateTypeData


class TemplateTypeCreationUseCase:

    def get_repository_info_by_project(self, project):
        setup = {"repositories": []}
        p_intelligence_queryset = ProjectIntelligence.objects.filter(project=project)
        for project_intelligence in p_intelligence_queryset:
            setup["repositories"].append({"uuid": str(project_intelligence.repository.uuid)})
        return setup

    def create_template_type(self, template_type_dto: TemplateTypeDTO):
        try:
            project = Project.objects.get(uuid=template_type_dto.project_uuid)
        except Project.DoesNotExist:
            raise InvalidTemplateTypeData(f"Project `{template_type_dto.project_uuid}` does not exists!")
        setup = self.get_repository_info_by_project_uuid(project)
        template_type, created = TemplateType.objects.get_or_create(uuid=template_type_dto.uuid, defaults=dict(name=template_type_dto.name, setup=setup))
        if not created:
            template_type.setup = setup
            template_type.name = template_type_dto.name
            template_type.save()
        return template_type
