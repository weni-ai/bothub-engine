from django_filters import rest_framework as filters
from django.utils.translation import gettext as _

from bothub.common.models import RepositoryEvaluate


class EvaluatesFilter(filters.FilterSet):
    class Meta:
        model = RepositoryEvaluate
        fields = [
            'text',
            'language',
            'intent',
        ]

    language = filters.CharFilter(
        field_name='language',
        method='filter_language',
        help_text=_('Language'))

    def filter_language(self, queryset, name, value):
        return queryset.filter(repository_update__language=value)
