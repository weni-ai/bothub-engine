from typing import Tuple

from bothub.common.models import Organization, OrganizationAuthorization, User
from bothub.authorizations.usecases.dto import OrgAuthDTO

class UserDoesNotExist(BaseException):
    pass

class OrgDoesNotExist(BaseException):
    pass


class AuthorizationsUsecase:
    def dispatch(self, action: str):
        if action == "create":
            return self.get_or_create_organization_authorization
        if action == "update":
            return self.update_organization_authorization
        if action == "delete":
            return self.delete_organization_authorization

    def __get_user(self, user_email: str) -> User:
        try:
            return User.objects.get(email=user_email)
        except User.DoesNotExist:
            return User.objects.create(email=user_email)

    def __get_org(self, org_id: int) -> Organization:
        try:
            return Organization.objects.get(id=org_id)
        except Organization.DoesNotExist:
            raise OrgDoesNotExist(f"Org with id {org_id} does not exist")

    def get_or_create_organization_authorization(self, org_auth_dto: OrgAuthDTO) -> Tuple[bool, OrganizationAuthorization]:
        org: Organization = self.__get_org(org_auth_dto.org_id)
        user: User = self.__get_user(org_auth_dto.user)

        try:
            org_auth: OrganizationAuthorization = org.organization_authorizations.get(user=user)
            return False, org_auth
        except OrganizationAuthorization.DoesNotExist:
            org_auth = org.organization_authorizations.create(
                user=user,
                role=org_auth_dto.role
            )
            return True, org_auth

    def update_organization_authorization(self, org_auth_dto: OrgAuthDTO) -> OrganizationAuthorization:
        created, org_auth = self.get_or_create_organization_authorization(org_auth_dto)

        if created:
            return org_auth

        org_auth.role = org_auth_dto.role
        org_auth.save(update_fields=["role"])

        return org_auth
    
    def delete_organization_authorization(self, org_auth_dto: OrgAuthDTO) -> None:
        _, org_auth = self.get_or_create_organization_authorization(org_auth_dto)
        org_auth.delete()
        return
