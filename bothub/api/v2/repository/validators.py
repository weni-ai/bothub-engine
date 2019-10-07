from rest_framework.exceptions import PermissionDenied
from django.utils.translation import gettext as _
from rest_framework.exceptions import ValidationError

from bothub.common.models import RepositoryExample


class CanContributeInRepositoryExampleValidator(object):
    def __call__(self, value):
        repository = value.repository_update.repository
        user_authorization = repository.get_user_authorization(self.request.user)
        if not user_authorization.check_permission('view.repositorytranslatedexample'):
            raise PermissionDenied(_("You can't contribute in this repository"))

    def set_context(self, serializer):
        self.request = serializer.context.get("request")


class CanContributeInRepositoryTranslatedExampleValidator(object):
    def __call__(self, value):
        repository = value.original_example.repository_update.repository
        user_authorization = repository.get_user_authorization(self.request.user)
        if not user_authorization.check_permission('view.repositorytranslatedexample'):
            raise PermissionDenied(_("You can't contribute in this repository"))

    def set_context(self, serializer):
        self.request = serializer.context.get("request")


class CanContributeInRepositoryValidator(object):
    def __call__(self, value):
        user_authorization = value.get_user_authorization(self.request.user)
        if not user_authorization.check_permission('write.repositoryexample'):
            raise PermissionDenied(_("You can't contribute in this repository"))

    def set_context(self, serializer):
        self.request = serializer.context.get("request")


class ExampleWithIntentOrEntityValidator(object):
    def __call__(self, attrs):
        intent = attrs.get("intent")
        entities = attrs.get("entities")

        if not intent and not entities:
            raise ValidationError(_("Define a intent or one entity"))


class IntentAndSentenceNotExistsValidator(object):
    def __call__(self, attrs):
        repository = attrs.get("repository")
        intent = attrs.get("intent")
        sentence = attrs.get("text")

        if RepositoryExample.objects.filter(
            text=sentence, intent=intent, repository_update__repository=repository
        ).count():
            raise ValidationError(_("Intention and Sentence already exists"))


class EntityNotEqualLabelValidator(object):
    def __call__(self, attrs):
        entity = attrs.get("entity")
        label = attrs.get("label")

        if entity == label:
            raise ValidationError(
                {"label": _("Label name can't be equal to entity name")}
            )
