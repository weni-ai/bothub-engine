from django.utils.translation import gettext as _
from django.core.exceptions import ValidationError as DjangoValidationError
from django_filters import rest_framework as filters

from rest_framework.exceptions import PermissionDenied
from rest_framework.exceptions import NotFound

from bothub.common.models import Repository
from bothub.common.models import RepositoryEvaluate
from bothub.common.models import RepositoryEvaluateResult


class EvaluatesFilter(filters.FilterSet):

    class Meta:
        model = RepositoryEvaluate
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
        help_text=_(
            'Filter evaluations with entities with a specific label.'
        )
    )

    entity = filters.CharFilter(
        field_name='entity',
        method='filter_entity',
        help_text=_('Filter evaluations with an entity.'))

    def filter_repository_uuid(self, queryset, name, value):
        request = self.request
        try:
            repository = Repository.objects.get(uuid=value)
            authorization = repository.get_user_authorization(request.user)
            if not authorization.can_read:
                raise PermissionDenied()
            return repository.evaluations(queryset=queryset)
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


class EvaluateResultsFilter(filters.FilterSet):

    class Meta:
        model = RepositoryEvaluateResult
        fields = []

    repository_uuid = filters.CharFilter(
        field_name='repository_uuid',
        method='filter_repository_uuid',
        required=True,
        help_text=_('Repository\'s UUID'))

    def filter_repository_uuid(self, queryset, name, value):
        request = self.request
        try:
            repository = Repository.objects.get(uuid=value)
            authorization = repository.get_user_authorization(request.user)

            if not authorization.can_read:
                raise PermissionDenied()
            return repository.evaluations_results(queryset=queryset)
        except Repository.DoesNotExist:
            raise NotFound(
                _('Repository {} does not exist').format(value))
        except DjangoValidationError:
            raise NotFound(_('Invalid repository_uuid'))


class EvaluateResultFilter(filters.FilterSet):

    class Meta:
        model = RepositoryEvaluateResult
        fields = []

    text = filters.CharFilter(
        field_name='text',
        method='filter_evaluate_text',
        required=False,
        help_text=_('Evaluate Text'))

    repository_uuid = filters.CharFilter(
        field_name='repository_uuid',
        method='filter_repository_uuid',
        required=True,
        help_text=_('Repository\'s UUID'))

    def filter_evaluate_text(self, queryset, name, value):
        return queryset.filter(log__icontains=value)

    def filter_repository_uuid(self, queryset, name, value):
        request = self.request
        try:
            repository = Repository.objects.get(uuid=value)
            authorization = repository.get_user_authorization(request.user)

            if not authorization.can_read:
                raise PermissionDenied()
            return repository.evaluations_results(queryset=queryset)
        except Repository.DoesNotExist:
            raise NotFound(
                _('Repository {} does not exist').format(value))
        except DjangoValidationError:
            raise NotFound(_('Invalid repository_uuid'))
