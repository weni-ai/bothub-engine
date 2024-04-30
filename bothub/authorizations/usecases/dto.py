from dataclasses import dataclass


@dataclass
class OrgAuthDTO:
    user: str
    role: int
    org_id: int
