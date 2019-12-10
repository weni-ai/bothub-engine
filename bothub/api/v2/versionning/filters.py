from django.core.exceptions import ValidationError as DjangoValidationError
from django.utils.translation import gettext as _
from django_filters import rest_framework as filters
from rest_framework.exceptions import NotFound
from rest_framework.exceptions import PermissionDenied

from bothub.common.models import Repository, RepositoryVersion


class VersioningFilter(filters.FilterSet):
    class Meta:
        model = RepositoryVersion
        fields = ["repository"]

    repository = filters.CharFilter(
        field_name="repository",
        method="filter_repository_uuid",
        required=True,
        help_text=_("Repository's UUID"),
    )

    def filter_repository_uuid(self, queryset, name, value):
        request = self.request
        try:
            repository = Repository.objects.get(uuid=value)
            authorization = repository.get_user_authorization(request.user)
            if not authorization.can_read:
                raise PermissionDenied()
            return RepositoryVersion.objects.filter(repository=repository)
        except Repository.DoesNotExist:
            raise NotFound(_("Repository {} does not exist").format(value))
        except DjangoValidationError:
            raise NotFound(_("Invalid repository_uuid"))
