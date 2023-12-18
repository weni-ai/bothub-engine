from bothub.common.models import Organization, OrganizationAuthorization
from bothub.authentication.models import User
from bothub.project.usecases.exceptions import InvalidOrganizationData


class OrganizationAuthorizationCreateUsecase:

    def get_or_create_user_by_email(self, email: str) -> tuple:
        return User.objects.get_or_create(email=email)

    def get_or_create_organization_authorization(
            self,
            organization: Organization,
            user: User,
            role: int
    ) -> OrganizationAuthorization:

        return OrganizationAuthorization.objects.get_or_create(
            organization=organization,
            user=user,
            role=role
        )

    def get_organization_by_id(self, organization_id) -> Organization:
        try:
            return Organization.objects.get(pk=organization_id)
        except Organization.DoesNotExist:
            raise InvalidOrganizationData(f"Organization {organization_id} does not exists!")

    def eda_consume_organization_authorization(
            self,
            authorizations: list,
            organization_id: int,
    ):

        organization = self.get_organization_by_id(organization_id)

        for authorization in authorizations:
            user, _ = self.get_or_create_user_by_email(authorization.get("user_email"))
            self.get_or_create_organization_authorization(
                organization=organization,
                user=user,
                role=authorization.get("role")
            )
