from ..models import TemplateType, Project, ProjectIntelligence


def create_template_type(uuid: str, project_uuid: Project, name: str) -> TemplateType:
    setup = {"repositories": []}

    for project_intelligence in ProjectIntelligence.objects.filter(project_uuid=project_uuid):
        try:
            setup["repositories"].append(project_intelligence.repositories.uuid)
        except NotImplementedError as error:
            print(error)

    template_type, created = TemplateType.objects.get_or_create(uuid=uuid, defaults=dict(name=name, setup=setup))

    if not created:
        template_type.name = name
        template_type.setup = setup
        template_type.save()

    return template_type
