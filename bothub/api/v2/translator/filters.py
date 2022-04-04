from django.db.models import Count, F
from django.db.models import Q
from django.utils.translation import ugettext_lazy as _
from django_filters import rest_framework as filters
from rest_framework.exceptions import PermissionDenied, NotFound
from django.core.exceptions import ValidationError as DjangoValidationError

from bothub.common.models import (
    RepositoryExample,
    RepositoryTranslator,
    Repository,
    RepositoryTranslatedExample,
)

from bothub.utils import filter_validate_entities


class RepositoryTranslatorFilter(filters.FilterSet):
    class Meta:
        model = RepositoryTranslator
        fields = ["repository"]

    repository = filters.CharFilter(
        field_name="repository",
        method="filter_repository_uuid",
        help_text=_("Repository's UUID"),
        required=True,
    )

    def filter_repository_uuid(self, queryset, name, value):
        request = self.request
        try:
            repository = Repository.objects.get(uuid=value)
            authorization = repository.get_user_authorization(request.user)
            if not authorization.is_admin:
                raise PermissionDenied()
            return queryset.filter(
                repository_version_language__repository_version__repository=repository
            )
        except Repository.DoesNotExist:
            raise NotFound(_("Repository {} does not exist").format(value))
        except DjangoValidationError:
            raise NotFound(_("Invalid repository UUID"))


class TranslatorExamplesFilter(filters.FilterSet):
    class Meta:
        model = RepositoryExample
        fields = ["text"]

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


class TranslationsTranslatorFilter(filters.FilterSet):
    class Meta:
        model = RepositoryTranslatedExample
        fields = []

    original_example_id = filters.CharFilter(
        field_name="original_example",
        method="filter_original_example_id",
        help_text="Filter by original example id",
    )

    def filter_original_example_id(self, queryset, name, value):
        return queryset.filter(original_example__pk=value)
