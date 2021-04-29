from django.core.exceptions import ValidationError as DjangoValidationError
from django.db.models import Q
from django.utils.translation import ugettext_lazy as _
from django_filters import rest_framework as filters
from rest_framework.exceptions import NotFound
from rest_framework.exceptions import PermissionDenied

from bothub.common.models import (
    Repository,
    RepositoryNLPLog,
    RepositoryEntity,
    RepositoryQueueTask,
    RepositoryIntent,
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

    repository_version = filters.CharFilter(
        field_name="repository_version_language",
        method="filter_repository_version",
        help_text=_("Filter for examples with version id."),
    )

    repository_version_language = filters.CharFilter(
        field_name="repository_version_language",
        method="filter_repository_version_language",
        help_text=_("Filter for examples with version language id."),
    )

    intent = filters.CharFilter(
        field_name="repository_version_language",
        method="filter_intent",
        help_text=_("Filter for examples with version name."),
    )

    confidence = filters.RangeFilter(
        field_name="repository_version_language", method="filter_confidence"
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

    def filter_repository_version(self, queryset, name, value):
        return queryset.filter(repository_version_language__repository_version=value)

    def filter_repository_version_language(self, queryset, name, value):
        return queryset.filter(repository_version_language=value)

    def filter_intent(self, queryset, name, value):
        return queryset.filter(
            repository_nlp_log__intent=value, repository_nlp_log__is_default=True
        )

    def filter_confidence(self, queryset, name, value):
        query = queryset.filter(
            Q(repository_nlp_log__confidence__gte=int(value.start) / 100),
            Q(repository_nlp_log__confidence__lte=int(value.stop) / 100),
        )
        return query


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


class RepositoryQueueTaskFilter(filters.FilterSet):
    class Meta:
        model = RepositoryQueueTask
        fields = ["repository_uuid", "repository_version"]

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

    type_processing = filters.ChoiceFilter(
        field_name="type_processing",
        method="filter_type_processing",
        choices=RepositoryQueueTask.TYPE_PROCESSING_CHOICES,
        help_text=_("Choose the type of processing"),
    )
    id_queue = filters.CharFilter(
        field_name="id_queue",
        method="filter_id_queue",
        help_text=_("Filter by Queue ID"),
    )

    def filter_repository_uuid(self, queryset, name, value):
        request = self.request
        try:
            repository = Repository.objects.get(uuid=value)
            authorization = repository.get_user_authorization(request.user)
            if not authorization.can_translate:
                raise PermissionDenied()
            return queryset.filter(
                repositoryversionlanguage__repository_version__repository=repository
            )
        except Repository.DoesNotExist:
            raise NotFound(_("Repository {} does not exist").format(value))
        except DjangoValidationError:
            raise NotFound(_("Invalid repository UUID"))

    def filter_repository_version(self, queryset, name, value):
        return queryset.filter(
            repositoryversionlanguage__repository_version=value
        ).order_by("-pk")

    def filter_type_processing(self, queryset, name, value):
        return queryset.filter(type_processing=value)

    def filter_id_queue(self, queryset, name, value):
        return queryset.filter(id_queue=value)


class RepositoryNLPLogReportsFilter(filters.FilterSet):
    class Meta:
        model = Repository
        fields = []

    start_date = filters.DateFilter(
        field_name="start_date", method="filter_start_date", required=True
    )
    end_date = filters.DateFilter(
        field_name="end_date", method="filter_end_date", required=True
    )
    organization_nickname = filters.CharFilter(
        field_name="user", method="filter_organization_nickname"
    )

    def filter_start_date(self, queryset, name, value):
        return queryset

    def filter_end_date(self, queryset, name, value):
        return queryset

    def filter_organization_nickname(self, queryset, name, value):
        return queryset


class RepositoryIntentFilter(filters.FilterSet):
    class Meta:
        model = RepositoryIntent
        fields = ["repository_version", "repository_version__repository"]

    repository_version = filters.CharFilter(
        required=True, help_text=_("Filter intents with version id.")
    )

    repository_version__repository = filters.CharFilter(
        required=True, help_text=_("Repository's UUID")
    )
