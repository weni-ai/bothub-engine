from django.core.exceptions import ValidationError as DjangoValidationError
from django.utils.translation import ugettext_lazy as _
from django_filters import rest_framework as filters
from rest_framework.exceptions import NotFound
from rest_framework.exceptions import PermissionDenied

from bothub.common.models import OrganizationAuthorization, Organization


class OrganizationAuthorizationFilter(filters.FilterSet):
    class Meta:
        model = OrganizationAuthorization
        fields = ["organization"]

    org_nickname = filters.CharFilter(
        field_name="organization",
        method="filter_organization_nickname",
        required=True,
        help_text=_("Organization Nickname"),
    )

    def filter_organization_nickname(self, queryset, name, value):
        request = self.request
        try:
            org = Organization.objects.get(nickname=value)
            authorization = org.get_organization_authorization(request.user)
            if not authorization.is_admin:
                raise PermissionDenied()
            return queryset.filter(organization=org)
        except Organization.DoesNotExist:
            raise NotFound(_("Organization {} does not exist").format(value))
        except DjangoValidationError:
            raise NotFound(_("Invalid organization UUID"))
