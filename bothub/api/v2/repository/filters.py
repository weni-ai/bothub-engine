from django.core.exceptions import ValidationError as DjangoValidationError
from django.utils.translation import ugettext_lazy as _
from django_filters import rest_framework as filters
from rest_framework.exceptions import NotFound
from rest_framework.exceptions import PermissionDenied

from bothub.common.models import (
    Repository,
    RepositoryNLPLog,
    RepositoryEntity,
)
from bothub.common.models import RepositoryAuthorization
from bothub.common.models import RequestRepositoryAuthorization


class RepositoriesFilter(filters.FilterSet):
    class Meta:
        model = Repository
        fields = ["name", "categories"]

    language = filters.CharFilter(
        field_name="language", method="filter_language", help_text=_("Language")
    )

    def filter_language(self, queryset, name, value):
        return queryset.supported_language(value)


class RepositoryAuthorizationFilter(filters.FilterSet):
    class Meta:
        model = RepositoryAuthorization
        fields = ["repository"]

    repository = filters.CharFilter(
        field_name="repository",
        method="filter_repository_uuid",
        help_text=_("Repository's UUID"),
    )

    def filter_repository_uuid(self, queryset, name, value):
        request = self.request
        try:
            repository = Repository.objects.get(uuid=value)
            authorization = repository.get_user_authorization(request.user)
            if not authorization.is_admin:
                raise PermissionDenied()
            return queryset.filter(repository=repository)
        except Repository.DoesNotExist:
            raise NotFound(_("Repository {} does not exist").format(value))
        except DjangoValidationError:
            raise NotFound(_("Invalid repository UUID"))


class RepositoryAuthorizationRequestsFilter(filters.FilterSet):
    class Meta:
        model = RequestRepositoryAuthorization
        fields = ["repository_uuid"]

    repository_uuid = filters.CharFilter(
        field_name="repository_uuid",
        required=True,
        method="filter_repository_uuid",
        help_text=_("Repository's UUID"),
    )

    def filter_repository_uuid(self, queryset, name, value):
        request = self.request
        try:
            repository = Repository.objects.get(uuid=value)
            authorization = repository.get_user_authorization(request.user)
            if not authorization.is_admin:
                raise PermissionDenied()
            return queryset.filter(repository=repository)
        except Repository.DoesNotExist:
            raise NotFound(_("Repository {} does not exist").format(value))
        except DjangoValidationError:
            raise NotFound(_("Invalid repository UUID"))


class RepositoryNLPLogFilter(filters.FilterSet):
    class Meta:
        model = RepositoryNLPLog
        fields = []

    repository_uuid = filters.CharFilter(
        field_name="repository_uuid",
        method="filter_repository_uuid",
        required=True,
        help_text=_("Repository's UUID"),
    )

    language = filters.CharFilter(
        field_name="language",
        method="filter_language",
        help_text="Filter by language, default is repository base language",
    )

    repository_version_name = filters.CharFilter(
        field_name="repository_version_language",
        method="filter_repository_version_by_name",
        help_text=_("Filter for examples with version name."),
    )

    intent = filters.CharFilter(
        field_name="repository_version_language",
        method="filter_intent",
        help_text=_("Filter for examples with version name."),
    )

    def filter_repository_uuid(self, queryset, name, value):
        request = self.request
        try:
            repository = Repository.objects.get(uuid=value)
            authorization = repository.get_user_authorization(request.user)
            if not authorization.can_contribute:
                raise PermissionDenied()
            return queryset.filter(
                repository_version_language__repository_version__repository=repository
            )
        except Repository.DoesNotExist:
            raise NotFound(_("Repository {} does not exist").format(value))
        except DjangoValidationError:
            raise NotFound(_("Invalid repository_uuid"))

    def filter_language(self, queryset, name, value):
        return queryset.filter(repository_version_language__language=value)

    def filter_repository_version_by_name(self, queryset, name, value):
        return queryset.filter(
            repository_version_language__repository_version__name=value
        )

    def filter_intent(self, queryset, name, value):
        return queryset.filter(
            repository_nlp_log__intent=value, repository_nlp_log__is_default=True
        )


class RepositoryEntitiesFilter(filters.FilterSet):
    class Meta:
        model = RepositoryEntity
        fields = ["repository_uuid", "repository_version", "value"]

    repository_uuid = filters.UUIDFilter(
        field_name="repository_uuid",
        required=True,
        method="filter_repository_uuid",
        help_text=_("Repository's UUID"),
    )

    repository_version = filters.CharFilter(
        field_name="repository_version",
        required=True,
        method="filter_repository_version",
        help_text=_("Repository Version ID"),
    )

    def filter_repository_uuid(self, queryset, name, value):
        request = self.request
        try:
            repository = Repository.objects.get(uuid=value)
            authorization = repository.get_user_authorization(request.user)
            if not authorization.can_translate:
                raise PermissionDenied()
            return queryset.filter(repository_version__repository=repository)
        except Repository.DoesNotExist:
            raise NotFound(_("Repository {} does not exist").format(value))
        except DjangoValidationError:
            raise NotFound(_("Invalid repository UUID"))

    def filter_repository_version(self, queryset, name, value):
        return queryset.filter(repository_version=value)
