from rest_framework.exceptions import NotFound
from rest_framework.exceptions import PermissionDenied
from django.utils.translation import gettext as _
from django.core.exceptions import ValidationError as DjangoValidationError
from django_filters import rest_framework as filters

from bothub.common.models import Repository
from bothub.common.models import RepositoryTranslatedExample


class TranslationsFilter(filters.FilterSet):
    class Meta:
        model = RepositoryTranslatedExample
        fields = []

    repository_uuid = filters.CharFilter(
        field_name="repository_uuid",
        method="filter_repository_uuid",
        required=True,
        help_text=_("Repository's UUID"),
    )
    from_language = filters.CharFilter(
        field_name="language",
        method="filter_from_language",
        help_text="Filter by original language",
    )
    to_language = filters.CharFilter(
        field_name="language",
        method="filter_to_language",
        help_text="Filter by translated language",
    )

    def filter_repository_uuid(self, queryset, name, value):
        request = self.request
        try:
            repository = Repository.objects.get(uuid=value)
            authorization = repository.get_user_authorization(request.user)
            if not authorization.check_permission("view.repositorytranslatedexample"):
                raise PermissionDenied()
            return RepositoryTranslatedExample.objects.filter(
                original_example__repository_update__repository=repository
            )
        except Repository.DoesNotExist:
            raise NotFound(_("Repository {} does not exist").format(value))
        except DjangoValidationError:
            raise NotFound(_("Invalid repository_uuid"))

    def filter_from_language(self, queryset, name, value):
        return queryset.filter(original_example__repository_update__language=value)

    def filter_to_language(self, queryset, name, value):
        return queryset.filter(language=value)
