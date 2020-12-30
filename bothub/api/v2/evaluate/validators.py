from django.utils.translation import ugettext_lazy as _
from rest_framework.exceptions import ValidationError

from bothub.common.models import RepositoryExample, RepositoryEvaluate


class ThereIsIntentValidator(object):
    def __call__(self, attrs):
        repository_version = attrs.get("repository_version_language")
        queryset = RepositoryExample.objects.filter(
            repository_version_language__repository_version=repository_version
        )
        if attrs.get("intent") not in attrs.get("repository").intents(
            queryset=queryset, version_default=repository_version.is_default
        ):
            raise ValidationError(_("Intent MUST match existing intents for training."))


class ThereIsEntityValidator(object):
    def __call__(self, attrs):
        entities = attrs.get("entities")
        repository_version = attrs.get("repository_version_language")

        if entities:
            entities_list = list(
                set(map(lambda x: x.get("entity"), attrs.get("entities")))
            )
            repository_entities_list = repository_version.entities.filter(
                value__in=entities_list
            )

            if len(entities_list) != len(repository_entities_list):
                raise ValidationError(
                    {
                        "entities": _(
                            "Entities MUST match existing entities for training."
                        )
                    }
                )


class ThereIsExistingSentenceValidator(object):
    def __call__(self, attrs):
        text = attrs.get("text")
        intent = attrs.get("intent")
        language = attrs.get("language")
        repository_version = attrs.get("repository_version_language")

        queryset = RepositoryEvaluate.objects.filter(
            repository_version_language__language=language,
            repository_version_language__repository_version=repository_version,
            text=text,
            intent=intent,
        )
        if queryset:
            raise ValidationError(_("You already have this phrase in your tests"))
