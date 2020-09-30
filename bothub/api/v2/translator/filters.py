from django.db.models import Count
from django.db.models import Q
from django.utils.translation import ugettext_lazy as _
from django_filters import rest_framework as filters

from bothub.common.models import RepositoryExample


class TranslatorExamplesFilter(filters.FilterSet):
    class Meta:
        model = RepositoryExample
        fields = ["text"]

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

    def filter_group(self, queryset, name, value):
        if value == "other":
            return queryset.filter(entities__entity__group__isnull=True)
        return queryset.filter(entities__entity__group__value=value)

    def filter_entity(self, queryset, name, value):
        return queryset.filter(entities__entity__value=value).distinct()

    def filter_entity_id(self, queryset, name, value):
        return queryset.filter(entities__entity__pk=value).distinct()

    def filter_intent(self, queryset, name, value):
        return queryset.filter(intent__text=value)

    def filter_intent_id(self, queryset, name, value):
        return queryset.filter(intent__pk=value)
