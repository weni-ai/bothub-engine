from django_filters import rest_framework as filters

from bothub.common.models import Repository


class RepositoriesFilter(filters.FilterSet):
    class Meta:
        model = Repository
        fields = [
            'name',
            'categories',
        ]
