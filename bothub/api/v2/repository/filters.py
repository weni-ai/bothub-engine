from django_filters import rest_framework as filters
from django.utils.translation import gettext as _

from bothub.common.models import Repository


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
        help_text=_('Language'))

    def filter_language(self, queryset, name, value):
        return queryset.supported_language(value)
