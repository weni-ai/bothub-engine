from django.utils.translation import gettext as _
from django.conf import settings
from django.core.exceptions import ValidationError


LANGUAGE_EN = 'en'
LANGUAGE_DE = 'de'
LANGUAGE_ES = 'es'
LANGUAGE_PT = 'pt'
LANGUAGE_FR = 'fr'
LANGUAGE_IT = 'it'
LANGUAGE_NL = 'nl'

VERBOSE_LANGUAGES = {
    LANGUAGE_EN: _('English'),
    LANGUAGE_DE: _('German'),
    LANGUAGE_ES: _('Spanish'),
    LANGUAGE_PT: _('Portuguese'),
    LANGUAGE_FR: _('French'),
    LANGUAGE_IT: _('Italian'),
    LANGUAGE_NL: _('Dutch'),
}

LANGUAGE_CHOICES = [
    (l, VERBOSE_LANGUAGES.get(l, l)) for l in
    settings.SUPPORTED_LANGUAGES
]


def is_valid_language(value):
    return value in settings.SUPPORTED_LANGUAGES.keys()


def validate_language(value):
    if not is_valid_language(value):
        raise ValidationError(_(
            '{} is not a supported language.').format(value))
