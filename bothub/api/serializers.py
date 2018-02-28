from rest_framework import serializers
from rest_framework.exceptions import NotFound
from rest_framework.exceptions import ValidationError
from django.utils.translation import gettext as _
from django.core.exceptions import ValidationError as DjangoValidationError

from bothub.common.models import Repository
from bothub.common.models import RepositoryUpdate
from bothub.common.models import RepositoryExample
from bothub.common.models import RepositoryExampleEntity
from bothub.common.models import RepositoryAuthorization


# Defaults

class CurrentUpdateDefault(object):
    def set_context(self, serializer_field):
        request = serializer_field.context['request']
        repository_uuid = request.POST.get('repository_uuid')
        
        if not repository_uuid:
            raise ValidationError(_('repository_uuid is required'))
        
        try:
            repository = Repository.objects.get(uuid=repository_uuid)
        except Repository.DoesNotExist:
            raise NotFound(_('Repository {} does not exist').format(repository_uuid))
        except DjangoValidationError:
            raise ValidationError(_('Invalid repository_uuid'))
        
        self.repository_update = repository.current_update

    def __call__(self):
        return self.repository_update

    def __repr__(self):
        return unicode_to_repr('%s()' % self.__class__.__name__)

class RepositoryExampleDefault(object):
    def set_context(self, serializer_field):
        request = serializer_field.context['request']
        repository_example_id = request.POST.get('repository_example_id')
        
        if not repository_example_id:
            raise ValidationError(_('repository_example_id is required'))
        
        try:
            self.repository_example = RepositoryExample.objects.get(id=repository_example_id)
        except RepositoryExample.DoesNotExist:
            raise NotFound(_('Repository example entity {} does not exist').format(repository_example_id))
        except DjangoValidationError:
            raise ValidationError(_('Invalid repository_example_id'))

    def __call__(self):
        return self.repository_example

    def __repr__(self):
        return unicode_to_repr('%s()' % self.__class__.__name__)


# Serializers

class RepositorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Repository
        fields = [
            'uuid',
            'owner',
            'slug',
            'is_private',
            'created_at',
        ]
    
    owner = serializers.PrimaryKeyRelatedField(
        read_only=True,
        default=serializers.CurrentUserDefault())

class CurrentRepositoryUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = RepositoryUpdate
        fields = [
            'id',
            'repository',
            'created_at',
        ]

class RepositoryExampleSerializer(serializers.ModelSerializer):
    class Meta:
        model = RepositoryExample
        fields = [
            'id',
            'repository_update',
            'deleted_in',
            'text',
            'intent',
            'created_at',
        ]
        read_only_fields = [
            'deleted_in',
        ]
    
    repository_update = serializers.PrimaryKeyRelatedField(
        read_only=True,
        default=CurrentUpdateDefault())

class RepositoryExampleEntitySerializer(serializers.ModelSerializer):
    class Meta:
        model = RepositoryExampleEntity
        fields = [
            'id',
            'repository_example',
            'start',
            'end',
            'entity',
            'created_at',
            'value',
        ]
    
    repository_example = serializers.PrimaryKeyRelatedField(
        read_only=True,
        default=RepositoryExampleDefault())
    value = serializers.SerializerMethodField()

    def get_value(self, obj):
        return obj.value

class RepositoryAuthorizationSerializer(serializers.ModelSerializer):
    class Meta:
        model = RepositoryAuthorization
        fields = [
            'uuid',
            'user',
            'repository',
            'created_at',
        ]
