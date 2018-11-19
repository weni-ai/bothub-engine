from django_filters import rest_framework as filters
from django.utils.translation import gettext as _
from django.db.models import Q

from bothub.common.models import Repository
from bothub.common.models import RepositoryUpdate
from bothub.common.models import RepositoryExample


class RepositoriesFilter(filters.FilterSet):
    class Meta:
        model = Repository
        fields = [
            'name',
            'categories',
        ]

    language = filters.CharFilter(
        field_name='language',
        method='filter_language',
        help_text=_('Repository\'s UUID'))

    def filter_language(self, queryset, name, value):
        valid_examples = RepositoryExample.objects.filter(
            deleted_in__isnull=True,
        )
        valid_updates = RepositoryUpdate.objects.filter(
            added__in=valid_examples,
        )
        return queryset.filter(
            Q(language=value)
            | Q(
                updates__in=valid_updates,
                updates__language=value,
            )
            | Q(
                updates__in=valid_updates,
                updates__added__translations__language=value,
            )
        )
