from django.core.exceptions import ValidationError as DjangoValidationError
from django.db.models import Count
from django.db.models import Q, F
from django.utils.translation import ugettext_lazy as _
from django_filters import rest_framework as filters
from rest_framework.exceptions import NotFound
from rest_framework.exceptions import PermissionDenied

from bothub.common.models import Repository
from bothub.common.models import RepositoryExample

from bothub.utils import filter_validate_entities


class ExamplesFilter(filters.FilterSet):
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
            if not authorization.can_translate:
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

    def filter_has_translation(self, queryset, name, value):
        annotated_queryset = queryset.annotate(translation_count=Count("translations"))
        if value:
            return annotated_queryset.filter(translation_count__gt=0)
        else:
            return annotated_queryset.filter(translation_count=0)

    def filter_has_not_translation_to(self, queryset, name, value):
        annotated_queryset = queryset.annotate(
            translation_count=Count(
                "translations", filter=Q(translations__language=value)
            )
        )
        return annotated_queryset.filter(translation_count=0)

    def filter_has_translation_to(self, queryset, name, value):
        annotated_queryset = queryset.annotate(
            translation_count=Count(
                "translations", filter=Q(translations__language=value)
            )
        )
        return annotated_queryset.filter(~Q(translation_count=0))

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

    def filter_has_valid_entities(self, queryset, name, value):
        return filter_validate_entities(queryset, name, value).filter(
            original_entities_count=F("entities_count")
        )

    def filter_has_invalid_entities(self, queryset, name, value):
        return filter_validate_entities(queryset, name, value).exclude(
            original_entities_count=F("entities_count")
        )
