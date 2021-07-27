from django.conf import settings
from django.core.exceptions import ValidationError as DjangoValidationError
from django.shortcuts import get_object_or_404
from django.utils.translation import ugettext_lazy as _
from django_filters import rest_framework as filters
from rest_framework.exceptions import NotFound
from rest_framework.exceptions import PermissionDenied
from bothub.authentication.models import RepositoryOwner
from bothub.common.models import (
    Repository,
    RepositoryEntity,
    RepositoryQueueTask,
    RepositoryIntent,
    OrganizationAuthorization,
    RepositoryVersion,
    RepositoryVersionLanguage,
)
from bothub.common.models import RepositoryAuthorization
from bothub.common.models import RequestRepositoryAuthorization


class RepositoriesFilter(filters.FilterSet):
    class Meta:
        model = Repository
        fields = ["name", "categories", "owner_id", "nickname"]

    language = filters.CharFilter(
        field_name="language", method="filter_language", help_text=_("Language")
    )
    owner_id = filters.CharFilter(
        method="filter_owner_id", help_text=_("Repository Owner Id")
    )
    nickname = filters.CharFilter(
        method="filter_nickname", help_text=_("Repository Owner Nickname")
    )

    def __filter_by_owner(self, queryset, owner):
        try:
            if owner.is_organization:
                auth_org = OrganizationAuthorization.objects.filter(
                    organization=owner, user=self.request.user
                ).first()
                if auth_org.can_read:
                    return queryset.filter(owner=owner).distinct()
            return queryset.filter(owner=owner, is_private=False).distinct()
        except TypeError:
            return queryset.none()

    def filter_language(self, queryset, name, value):
        return queryset.supported_language(value)

    def filter_owner_id(self, queryset, name, value):
        owner = get_object_or_404(RepositoryOwner, pk=value)
        return self.__filter_by_owner(queryset, owner)

    def filter_nickname(self, queryset, name, value):
        owner = get_object_or_404(RepositoryOwner, nickname=value)
        return self.__filter_by_owner(queryset, owner)


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


class RepositoryNLPLogFilter:
    def __init__(self, params, user):
        self.params = params
        self.user = user
        self.check = self.check_params()

    def check_params(self):
        validate_param = False
        # import pdb; pdb.set_trace()

        for param, value in self.params.items():
            if value is not None:
                validate_param = getattr(self, f"check_{param}")(value)
        return validate_param

    def check_repository_uuid(self, value):
        try:
            repository = Repository.objects.get(uuid=value)
            authorization = repository.get_user_authorization(self.user)
            if not authorization.can_contribute:
                raise PermissionDenied()
            return True
        except Repository.DoesNotExist:
            raise NotFound(_("Repository {} does not exist").format(value))
        except DjangoValidationError:
            raise NotFound(_("Invalid repository_uuid"))

    def check_repository_version(self, value):
        try:
            repository = RepositoryVersion.objects.get(pk=value).repository
            authorization = repository.get_user_authorization(self.user)
            if not authorization.can_contribute:
                raise PermissionDenied()
            return True
        except RepositoryVersion.DoesNotExist:
            raise NotFound(_("RepositoryVersion {} does not exist").format(value))
        except DjangoValidationError:
            raise NotFound(_("Invalid repository_version"))

    def check_repository_version_language(self, value):
        try:
            repository = RepositoryVersionLanguage.objects.get(
                pk=value
            ).repository_version.repository
            restrict_access_list = settings.REPOSITORY_RESTRICT_ACCESS_NLP_LOGS
            if (
                restrict_access_list != []
                and str(repository.uuid) not in restrict_access_list
            ):
                # Restricts log access to a particular or multiple intelligences
                raise PermissionDenied()
            authorization = repository.get_user_authorization(self.user)
            if not authorization.can_contribute:
                raise PermissionDenied()
            return True
        except RepositoryVersionLanguage.DoesNotExist:
            raise NotFound(
                _("RepositoryVersionLanguage {} does not exist").format(value)
            )
        except DjangoValidationError:
            raise NotFound(_("Invalid repository_version_language"))


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
