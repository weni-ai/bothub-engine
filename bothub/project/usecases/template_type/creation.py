from .template_type_dto import TemplateTypeDTO
from bothub.project.models import ProjectIntelligence, TemplateType


class TemplateTypeCreationUseCase:

    def get_setup_by_project_uuid(self, project_uuid):
        setup = {"repositories": []}
        p_intelligence_queryset = ProjectIntelligence.objects.filter(project__uuid=project_uuid)
        for project_intelligence in p_intelligence_queryset:
            setup["repositories"].append({"uuid": str(project_intelligence.repository.uuid)})
        return setup

    def create_template_type(self, template_type_dto: TemplateTypeDTO):
        setup = self.get_setup_by_project_uuid(template_type_dto.project_uuid)
        template_type, created = TemplateType.objects.get_or_create(uuid=template_type_dto.uuid, defaults=dict(name=template_type_dto.name, setup=setup))
        if not created:
            template_type.setup = setup
            template_type.name = template_type_dto.name
            template_type.save()
        return template_type
