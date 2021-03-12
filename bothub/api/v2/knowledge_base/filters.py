from django.utils.translation import ugettext_lazy as _
from django.core.exceptions import ValidationError as DjangoValidationError
from django_filters import rest_framework as filters
from rest_framework.exceptions import PermissionDenied, NotFound

from bothub.common.models import QAKnowledgeBase, Repository, QAContext


class QAKnowledgeBaseFilter(filters.FilterSet):
    class Meta:
        model = QAKnowledgeBase
        fields = ["title", "created_at", "repository_uuid"]

    repository_uuid = filters.CharFilter(
        field_name="repository_uuid",
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

            return queryset.filter(repository=repository)
        except Repository.DoesNotExist:
            raise NotFound(_("Repository {} does not exist").format(value))
        except DjangoValidationError:
            raise NotFound(_("Invalid repository_uuid"))


class QAContextFilter(filters.FilterSet):
    class Meta:
        model = QAContext
        fields = ["text", "language", "created_at", "repository_uuid", "knowledge_base_id"]

    knowledge_base_id = filters.CharFilter(field_name="knowledge_base__id")

    repository_uuid = filters.CharFilter(
        field_name="repository_uuid",
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

            return queryset.filter(knowledge_base__repository=repository)
        except Repository.DoesNotExist:
            raise NotFound(_("Repository {} does not exist").format(value))
        except DjangoValidationError:
            raise NotFound(_("Invalid repository_uuid"))
