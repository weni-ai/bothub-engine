from django.utils.translation import gettext as _

LANGUAGE_EN = 'en'
LANGUAGE_DE = 'de'
LANGUAGE_ES = 'es'
LANGUAGE_PT = 'pt'
LANGUAGE_FR = 'fr'
LANGUAGE_IT = 'it'
LANGUAGE_NL = 'nl'

LANGUAGE_CHOICES = [
    (LANGUAGE_EN, _('English')),
    (LANGUAGE_DE, _('German')),
    (LANGUAGE_ES, _('Spanish')),
    (LANGUAGE_PT, _('Portuguese')),
    (LANGUAGE_FR, _('French')),
    (LANGUAGE_IT, _('Italian')),
    (LANGUAGE_NL, _('Dutch')),
]

SUPPORTED_LANGUAGES = [
    LANGUAGE_EN,
    LANGUAGE_DE,
    LANGUAGE_ES,
    LANGUAGE_PT,
    LANGUAGE_FR,
    LANGUAGE_IT,
    LANGUAGE_NL,
]
