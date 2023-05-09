from django.core.exceptions import ValidationError as DjangoValidationError
from django.utils.translation import ugettext_lazy as _
from django_filters import rest_framework as filters
from rest_framework.exceptions import NotFound
from rest_framework.exceptions import PermissionDenied

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
    repository_version = filters.CharFilter(
        field_name="repository_version_language",
        method="filter_repository_version",
        help_text=_("Filter for examples with version id."),
    )
    original_example_id = filters.CharFilter(
        field_name="original_example",
        method="filter_original_example_id",
        help_text="Filter by original example id",
    )
    search = filters.CharFilter(
        field_name="search",
        method="filter_search",
        help_text="filter by text"
    )

    def filter_repository_uuid(self, queryset, name, value):
        request = self.request
        try:
            repository = Repository.objects.get(uuid=value)
            authorization = repository.get_user_authorization(request.user)
            if not authorization.can_read:
                raise PermissionDenied()
            if request.query_params.get("repository_version"):
                return RepositoryTranslatedExample.objects.filter(
                    original_example__repository_version_language__repository_version__repository=repository
                )
            return RepositoryTranslatedExample.objects.filter(
                original_example__repository_version_language__repository_version__repository=repository,
                repository_version_language__repository_version__is_default=True,
            )
        except Repository.DoesNotExist:
            raise NotFound(_("Repository {} does not exist").format(value))
        except DjangoValidationError:
            raise NotFound(_("Invalid repository_uuid"))

    def filter_from_language(self, queryset, name, value):
        return queryset.filter(
            original_example__repository_version_language__language=value
        )

    def filter_to_language(self, queryset, name, value):
        return queryset.filter(language=value)

    def filter_repository_version(self, queryset, name, value):
        return queryset.filter(
            repository_version_language__repository_version__pk=value
        )

    def filter_original_example_id(self, queryset, name, value):
        return queryset.filter(original_example__pk=value)

    def filter_search(self, queryset, name, value):
        return queryset.filter(text__icontains=value)
