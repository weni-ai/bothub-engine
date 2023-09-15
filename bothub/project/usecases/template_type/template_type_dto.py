from dataclasses import dataclass


@dataclass
class TemplateTypeDTO:
    uuid: str
    name: str
    project_uuid: str
