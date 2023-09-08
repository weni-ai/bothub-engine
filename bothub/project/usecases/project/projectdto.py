from dataclasses import dataclass
from django.contrib.auth import get_user_model


User = get_user_model()


@dataclass
class ProjectCreationDTO:
    uuid: str
    name: str
    is_template: bool
    date_format: str
    template_type_uuid: str
    timezone: str
    organization_id: int