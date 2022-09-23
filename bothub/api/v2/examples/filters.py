from django.core.exceptions import ValidationError as DjangoValidationError
from django.db.models import Count, Q
from django.utils.translation import ugettext_lazy as _
from django_filters import rest_framework as filters
from rest_framework.exceptions import NotFound
from rest_framework.exceptions import PermissionDenied

from bothub.common.models import Repository
from bothub.common.models import RepositoryExample

from bothub.api.v2 import READ_METHODS
from bothub.utils import DefaultExamplesFilter


class ExamplesFilter(DefaultExamplesFilter):
    class Meta:
        model = RepositoryExample
        fields = ["text", "language"]

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
    has_translation = filters.BooleanFilter(
        field_name="has_translation",
        method="filter_has_translation",
        help_text=_("Filter for examples with or without translation"),
    )
    has_not_translation_to = filters.CharFilter(
        field_name="has_not_translation_to", method="filter_has_not_translation_to"
    )
    has_translation_to = filters.CharFilter(
        field_name="has_translation_to", method="filter_has_translation_to"
    )
    is_available_language = filters.CharFilter(
        field_name="is_available_language", method="filter_is_available_language"
    )
    order_by_translation = filters.CharFilter(
        field_name="order_by_translation",
        method="filter_order_by_translation",
        help_text=_("Order examples with translation by language"),
    )
    group = filters.CharFilter(
        field_name="group",
        method="filter_group",
        help_text=_("Filter for examples with entities with specific group."),
    )
    entity = filters.CharFilter(
        field_name="entity",
        method="filter_entity",
        help_text=_("Filter for examples with entity."),
    )
    entity_id = filters.CharFilter(
        field_name="entity_id",
        method="filter_entity_id",
        help_text=_("Filter for examples with entity by id."),
    )
    repository_version = filters.CharFilter(
        field_name="repository_version_language",
        method="filter_repository_version",
        help_text=_("Filter for examples with version id."),
    )
    start_created_at = filters.DateTimeFilter(
        field_name="created_at",
        lookup_expr="gte",
        help_text=_("Filter by record creation date, example: 2020-08-15 15:35:12.51"),
    )
    end_created_at = filters.DateTimeFilter(
        field_name="created_at",
        lookup_expr="lte",
        help_text=_("Filter by record creation date, example: 2020-08-17 15:35:12.51"),
    )
    intent = filters.CharFilter(
        field_name="intent__text",
        method="filter_intent",
        help_text=_("Filter for examples with intent by text."),
    )
    intent_id = filters.CharFilter(
        field_name="intent__pk",
        method="filter_intent_id",
        help_text=_("Filter for examples with intent by id."),
    )
    has_valid_entities = filters.CharFilter(
        field_name="has_valid_entities",
        method="filter_has_valid_entities",
        help_text=_(
            "Filter all translations whose entities are valid, that is, the entities of the translations that match the entities of the original sentence"
        ),
    )
    has_invalid_entities = filters.CharFilter(
        field_name="has_invalid_entities",
        method="filter_has_invalid_entities",
        help_text=_(
            "Filter all translations whose entities are invalid, that is, the translation entities do not match the entities in the original sentence"
        ),
    )

    def filter_repository_uuid(self, queryset, name, value):
        request = self.request
        try:
            repository = Repository.objects.get(uuid=value)
            authorization = repository.get_user_authorization(request.user)
            if request.method not in READ_METHODS and not authorization.can_translate:
                raise PermissionDenied()
            if request.query_params.get("repository_version"):
                return queryset
            return repository.examples(queryset=queryset)
        except Repository.DoesNotExist:
            raise NotFound(_("Repository {} does not exist").format(value))
        except DjangoValidationError:
            raise NotFound(_("Invalid repository_uuid"))

    def filter_language(self, queryset, name, value):
        return queryset.filter(repository_version_language__language=value)

    def filter_repository_version(self, queryset, name, value):
        return queryset.filter(
            repository_version_language__repository_version__pk=value
        )

    def filter_is_available_language(self, queryset, name, value):
        annotated_queryset = queryset.annotate(
            translation_count=Count(
                "translations", filter=Q(translations__language=value)
            )
        )
        return annotated_queryset.filter(
            ~Q(translation_count=0) | Q(repository_version_language__language=value)
        )

    def filter_order_by_translation(self, queryset, name, value):
        inverted = value[0] == "-"
        language = value[1:] if inverted else value
        result_queryset = queryset.annotate(
            translation_count=Count(
                "translations", filter=Q(translations__language=language)
            )
        )
        result_queryset = result_queryset.order_by(
            "-translation_count" if inverted else "translation_count"
        )
        return result_queryset
