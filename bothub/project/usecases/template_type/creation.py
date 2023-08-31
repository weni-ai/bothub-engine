from .template_type_dto import TemplateTypeDTO
from bothub.project.models import ProjectIntelligence, TemplateType


class TemplateTypeCreationUseCase:

    def get_repository_info_by_project_uuid(self, project_uuid):
        info = {"repositories": []}
        p_intelligence_queryset = ProjectIntelligence.objects.filter(project__uuid=project_uuid)
        for project_intelligence in p_intelligence_queryset:
            info["repositories"].append(str(project_intelligence.repository.uuid))
        return info

    def create_template_type(self, template_type_dto: TemplateTypeDTO):
        try:
            setup = self.get_repository_info_by_project_uuid(template_type_dto.project_uuid)
            print("[ AI Template Type Consumer] get repositories info")
            template_type, created = TemplateType.objects.get_or_create(uuid=template_type_dto.uuid, defaults=dict(name=template_type_dto.name, setup=setup))
            if not created:
                template_type.setup = setup
                template_type.name = template_type_dto.name
                template_type.save()
            return template_type
        except Exception as err:
            print(f"Can't create project `{template_type_dto.project_uuid}`: {err}")
