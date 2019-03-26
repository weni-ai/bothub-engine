from django.utils.translation import gettext as _
from django.core.exceptions import ValidationError as DjangoValidationError
from django.db.models import Q
from django.db.models import Count
from rest_framework.exceptions import PermissionDenied
from rest_framework.exceptions import NotFound
from django_filters import rest_framework as filters

from bothub.common.models import Repository
from bothub.common.models import RepositoryValidation


class ValidationFilter(filters.FilterSet):
    class Meta:
        model = RepositoryValidation
        fields = [
            'text',
            'language',
            'intent',
        ]

    repository_uuid = filters.CharFilter(
        field_name='repository_uuid',
        method='filter_repository_uuid',
        required=True,
        help_text=_('Repository\'s UUID'))
    language = filters.CharFilter(
        field_name='language',
        method='filter_language',
        help_text='Filter by language, default is repository base language')
    label = filters.CharFilter(
        field_name='label',
        method='filter_label',
        help_text=_('Filter for validations with entities with specific label.'))
    entity = filters.CharFilter(
        field_name='entity',
        method='filter_entity',
        help_text=_('Filter for validations with entity.'))

    def filter_repository_uuid(self, queryset, name, value):
        request = self.request
        try:
            repository = Repository.objects.get(uuid=value)
            authorization = repository.get_user_authorization(request.user)
            if not authorization.can_read:
                raise PermissionDenied()
            return repository.validations(queryset=queryset)
        except Repository.DoesNotExist:
            raise NotFound(
                _('Repository {} does not exist').format(value))
        except DjangoValidationError:
            raise NotFound(_('Invalid repository_uuid'))

    def filter_language(self, queryset, name, value):
        return queryset.filter(repository_update__language=value)

    def filter_label(self, queryset, name, value):
        if value == 'other':
            return queryset.filter(entities__entity__label__isnull=True)
        return queryset.filter(entities__entity__label__value=value)

    def filter_entity(self, queryset, name, value):
        return queryset.filter(entities__entity__value=value)
