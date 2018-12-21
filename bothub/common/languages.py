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
LANGUAGE_PT_BR = 'pt_br'
LANGUAGE_ID = 'id'
LANGUAGE_MN = 'mn'
LANGUAGE_AR = 'ar'
LANGUAGE_BN = 'bn'
LANGUAGE_HI = 'hi'
LANGUAGE_RU = 'ru'
LANGUAGE_TH = 'th'
LANGUAGE_VI = 'vi'
LANGUAGE_KH = 'kh'
LANGUAGE_SW = 'sw'
LANGUAGE_CA = 'ca'
LANGUAGE_DA = 'da'
LANGUAGE_EL = 'el'
LANGUAGE_FA = 'fa'
LANGUAGE_FI = 'fi'
LANGUAGE_GA = 'ga'
LANGUAGE_HE = 'he'
LANGUAGE_HR = 'hr'
LANGUAGE_HU = 'hu'
LANGUAGE_JA = 'ja'
LANGUAGE_NB = 'nb'
LANGUAGE_PL = 'pl'
LANGUAGE_RO = 'ro'
LANGUAGE_SI = 'si'
LANGUAGE_SV = 'sv'
LANGUAGE_TE = 'te'
LANGUAGE_TR = 'tr'
LANGUAGE_TT = 'tt'
LANGUAGE_UR = 'ur'
LANGUAGE_ZH = 'zh'

VERBOSE_LANGUAGES = {
    LANGUAGE_EN: _('English'),
    LANGUAGE_DE: _('German'),
    LANGUAGE_ES: _('Spanish'),
    LANGUAGE_PT: _('Portuguese'),
    LANGUAGE_FR: _('French'),
    LANGUAGE_IT: _('Italian'),
    LANGUAGE_NL: _('Dutch'),
    LANGUAGE_PT_BR: _('Brazilian Portuguese'),
    LANGUAGE_ID: _('Indonesian'),
    LANGUAGE_MN: _('Mongolian'),
    LANGUAGE_AR: _('Arabic'),
    LANGUAGE_BN: _('Bengali'),
    LANGUAGE_HI: _('Hindi'),
    LANGUAGE_RU: _('Russian'),
    LANGUAGE_TH: _('Thai'),
    LANGUAGE_VI: _('Vietnamese'),
    LANGUAGE_KH: _('Khmer'),
    LANGUAGE_SW: _('Swahili'),
    LANGUAGE_CA: _('Catalan'),
    LANGUAGE_DA: _('Danish'),
    LANGUAGE_EL: _('Greek'),
    LANGUAGE_FA: _('Persian'),
    LANGUAGE_FI: _('Finnish'),
    LANGUAGE_GA: _('Irish'),
    LANGUAGE_HE: _('Hebrew'),
    LANGUAGE_HR: _('Croatian'),
    LANGUAGE_HU: _('Hungarian'),
    LANGUAGE_JA: _('Japanese'),
    LANGUAGE_NB: _('Norwegian'),
    LANGUAGE_PL: _('Polish'),
    LANGUAGE_RO: _('Romanian'),
    LANGUAGE_SI: _('Sinhala'),
    LANGUAGE_SV: _('Swedish'),
    LANGUAGE_TE: _('Telugu'),
    LANGUAGE_TR: _('Turkish'),
    LANGUAGE_TT: _('Tatar'),
    LANGUAGE_UR: _('Urdu'),
    LANGUAGE_ZH: _('Chinese'),
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
