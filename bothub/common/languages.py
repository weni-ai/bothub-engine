from django.utils.translation import ugettext_lazy as _
from django.conf import settings
from django.core.exceptions import ValidationError


LANGUAGE_EN = "en"
LANGUAGE_DE = "de"
LANGUAGE_ES = "es"
LANGUAGE_PT = "pt"
LANGUAGE_FR = "fr"
LANGUAGE_IT = "it"
LANGUAGE_NL = "nl"
LANGUAGE_PT_BR = "pt_br"
LANGUAGE_ID = "id"
LANGUAGE_MN = "mn"
LANGUAGE_AR = "ar"
LANGUAGE_BN = "bn"
LANGUAGE_HI = "hi"
LANGUAGE_RU = "ru"
LANGUAGE_TH = "th"
LANGUAGE_VI = "vi"
LANGUAGE_KH = "kh"
LANGUAGE_SW = "sw"
LANGUAGE_CA = "ca"
LANGUAGE_DA = "da"
LANGUAGE_EL = "el"
LANGUAGE_FA = "fa"
LANGUAGE_FI = "fi"
LANGUAGE_GA = "ga"
LANGUAGE_HE = "he"
LANGUAGE_HR = "hr"
LANGUAGE_HU = "hu"
LANGUAGE_JA = "ja"
LANGUAGE_NB = "nb"
LANGUAGE_PL = "pl"
LANGUAGE_RO = "ro"
LANGUAGE_SI = "si"
LANGUAGE_SV = "sv"
LANGUAGE_TE = "te"
LANGUAGE_TR = "tr"
LANGUAGE_TT = "tt"
LANGUAGE_UR = "ur"
LANGUAGE_ZH = "zh"
LANGUAGE_HA = "ha"
LANGUAGE_KA = "ka"
LANGUAGE_KK = "kk"
LANGUAGE_SQ = "sq"
LANGUAGE_HY = "hy"
LANGUAGE_AZ = "az"
LANGUAGE_BE = "be"
LANGUAGE_BS = "bs"
LANGUAGE_BG = "bg"
LANGUAGE_CS = "cs"
LANGUAGE_KY = "ky"
LANGUAGE_MK = "mk"
LANGUAGE_SR = "sr"
LANGUAGE_UK = "uk"
LANGUAGE_UZ = "uz"
LANGUAGE_AB = "ab"
LANGUAGE_AA = "aa"
LANGUAGE_AF = "af"
LANGUAGE_AK = "ak"
LANGUAGE_AM = "am"
LANGUAGE_AN = "an"
LANGUAGE_AS = "as"
LANGUAGE_AV = "av"
LANGUAGE_AE = "ae"
LANGUAGE_AY = "ay"
LANGUAGE_BM = "bm"
LANGUAGE_BA = "ba"
LANGUAGE_EU = "eu"
LANGUAGE_BH = "bh"
LANGUAGE_BI = "bi"
LANGUAGE_BR = "br"
LANGUAGE_MY = "my"
LANGUAGE_CH = "ch"
LANGUAGE_CE = "ce"
LANGUAGE_NY = "ny"
LANGUAGE_KW = "kw"
LANGUAGE_CV = "cv"
LANGUAGE_CO = "co"
LANGUAGE_CR = "cr"
LANGUAGE_DV = "dv"
LANGUAGE_DZ = "dz"
LANGUAGE_EO = "eo"
LANGUAGE_ET = "et"
LANGUAGE_EE = "ee"
LANGUAGE_FO = "fo"
LANGUAGE_FJ = "fj"
LANGUAGE_FF = "ff"
LANGUAGE_GL = "gl"
LANGUAGE_GU = "gu"
LANGUAGE_HT = "ht"
LANGUAGE_HZ = "hz"
LANGUAGE_HO = "ho"
LANGUAGE_IA = "ia"
LANGUAGE_IE = "ie"
LANGUAGE_IG = "ig"
LANGUAGE_IK = "ik"
LANGUAGE_IO = "io"
LANGUAGE_IS = "is"
LANGUAGE_IU = "iu"
LANGUAGE_JV = "jv"
LANGUAGE_KL = "kl"
LANGUAGE_KN = "kn"
LANGUAGE_KR = "kr"
LANGUAGE_KS = "ks"
LANGUAGE_KM = "km"
LANGUAGE_KI = "ki"
LANGUAGE_RW = "rw"
LANGUAGE_KV = "kv"
LANGUAGE_KG = "kg"
LANGUAGE_KO = "ko"
LANGUAGE_KU = "ku"
LANGUAGE_KJ = "kj"
LANGUAGE_LA = "la"
LANGUAGE_LB = "lb"
LANGUAGE_LG = "lg"
LANGUAGE_LI = "li"
LANGUAGE_LN = "ln"
LANGUAGE_LO = "lo"
LANGUAGE_LT = "lt"
LANGUAGE_LU = "lu"
LANGUAGE_LV = "lv"
LANGUAGE_GV = "gv"
LANGUAGE_MG = "mg"
LANGUAGE_MS = "ms"
LANGUAGE_ML = "ml"
LANGUAGE_MT = "mt"
LANGUAGE_MI = "mi"
LANGUAGE_MR = "mr"
LANGUAGE_MH = "mh"
LANGUAGE_NA = "na"
LANGUAGE_NV = "nv"
LANGUAGE_ND = "nd"
LANGUAGE_NE = "ne"
LANGUAGE_NG = "ng"
LANGUAGE_NN = "nn"
LANGUAGE_NO = "no"
LANGUAGE_II = "ii"
LANGUAGE_NR = "nr"
LANGUAGE_OC = "oc"
LANGUAGE_OJ = "oj"
LANGUAGE_CU = "cu"
LANGUAGE_OM = "om"
LANGUAGE_OR = "or"
LANGUAGE_OS = "os"
LANGUAGE_PA = "pa"
LANGUAGE_PI = "pi"
LANGUAGE_PS = "ps"
LANGUAGE_QU = "qu"
LANGUAGE_RM = "rm"
LANGUAGE_RN = "rn"
LANGUAGE_SA = "sa"
LANGUAGE_SC = "sc"
LANGUAGE_SD = "sd"
LANGUAGE_SE = "se"
LANGUAGE_SM = "sm"
LANGUAGE_SG = "sg"
LANGUAGE_GD = "gd"
LANGUAGE_SN = "sn"
LANGUAGE_SK = "sk"
LANGUAGE_SL = "sl"
LANGUAGE_SO = "so"
LANGUAGE_ST = "st"
LANGUAGE_SU = "su"
LANGUAGE_SS = "ss"
LANGUAGE_TA = "ta"
LANGUAGE_TG = "tg"
LANGUAGE_TI = "ti"
LANGUAGE_BO = "bo"
LANGUAGE_TK = "tk"
LANGUAGE_TL = "tl"
LANGUAGE_TN = "tn"
LANGUAGE_TO = "to"
LANGUAGE_TW = "tw"
LANGUAGE_TY = "ty"
LANGUAGE_UG = "ug"
LANGUAGE_VE = "ve"
LANGUAGE_VO = "vo"
LANGUAGE_WA = "wa"
LANGUAGE_CY = "cy"
LANGUAGE_WO = "wo"
LANGUAGE_FY = "fy"
LANGUAGE_XH = "xh"
LANGUAGE_YI = "yi"
LANGUAGE_YO = "yo"
LANGUAGE_ZA = "za"
LANGUAGE_ZU = "zu"


VERBOSE_LANGUAGES = {
    LANGUAGE_EN: _("English"),
    LANGUAGE_DE: _("German"),
    LANGUAGE_ES: _("Spanish"),
    LANGUAGE_PT: _("Portuguese"),
    LANGUAGE_FR: _("French"),
    LANGUAGE_IT: _("Italian"),
    LANGUAGE_NL: _("Dutch"),
    LANGUAGE_PT_BR: _("Brazilian Portuguese"),
    LANGUAGE_ID: _("Indonesian"),
    LANGUAGE_MN: _("Mongolian"),
    LANGUAGE_AR: _("Arabic"),
    LANGUAGE_BN: _("Bengali"),
    LANGUAGE_HI: _("Hindi"),
    LANGUAGE_RU: _("Russian"),
    LANGUAGE_TH: _("Thai"),
    LANGUAGE_VI: _("Vietnamese"),
    LANGUAGE_KH: _("Khmer"),
    LANGUAGE_SW: _("Swahili"),
    LANGUAGE_CA: _("Catalan"),
    LANGUAGE_DA: _("Danish"),
    LANGUAGE_EL: _("Greek"),
    LANGUAGE_FA: _("Persian"),
    LANGUAGE_FI: _("Finnish"),
    LANGUAGE_GA: _("Irish"),
    LANGUAGE_HE: _("Hebrew"),
    LANGUAGE_HR: _("Croatian"),
    LANGUAGE_HU: _("Hungarian"),
    LANGUAGE_JA: _("Japanese"),
    LANGUAGE_NB: _("Norwegian"),
    LANGUAGE_PL: _("Polish"),
    LANGUAGE_RO: _("Romanian"),
    LANGUAGE_SI: _("Sinhala"),
    LANGUAGE_SV: _("Swedish"),
    LANGUAGE_TE: _("Telugu"),
    LANGUAGE_TR: _("Turkish"),
    LANGUAGE_TT: _("Tatar"),
    LANGUAGE_UR: _("Urdu"),
    LANGUAGE_ZH: _("Chinese"),
    LANGUAGE_HA: _("Hausa"),
    LANGUAGE_KA: _("Georgian"),
    LANGUAGE_KK: _("Kazakh"),
    LANGUAGE_SQ: _("Albanian"),
    LANGUAGE_HY: _("Armenian"),
    LANGUAGE_AZ: _("Azerbaijani"),
    LANGUAGE_BE: _("Belarusian"),
    LANGUAGE_BS: _("Bosnian"),
    LANGUAGE_BG: _("Bulgarian"),
    LANGUAGE_CS: _("Czech"),
    LANGUAGE_KY: _("Kyrgyz"),
    LANGUAGE_MK: _("Macedonian"),
    LANGUAGE_SR: _("Serbian"),
    LANGUAGE_UK: _("Ukrainian"),
    LANGUAGE_UZ: _("Uzbek"),
    LANGUAGE_AB: _("Abkhazian"),
    LANGUAGE_AA: _("Afar"),
    LANGUAGE_AF: _("Afrikaans"),
    LANGUAGE_AK: _("Akan"),
    LANGUAGE_AM: _("Amharic"),
    LANGUAGE_AN: _("Aragonese"),
    LANGUAGE_AS: _("Assamese"),
    LANGUAGE_AV: _("Avaric"),
    LANGUAGE_AE: _("Avestan"),
    LANGUAGE_AY: _("Aymara"),
    LANGUAGE_BM: _("Bambara"),
    LANGUAGE_BA: _("Bashkir"),
    LANGUAGE_EU: _("Basque"),
    LANGUAGE_BH: _("Bihari languages"),
    LANGUAGE_BI: _("Bislama"),
    LANGUAGE_BR: _("Breton"),
    LANGUAGE_MY: _("Burmese"),
    LANGUAGE_CH: _("Chamorro"),
    LANGUAGE_CE: _("Chechen"),
    LANGUAGE_NY: _("Chichewa"),
    LANGUAGE_KW: _("Cornish"),
    LANGUAGE_CV: _("Chuvash"),
    LANGUAGE_CO: _("Corsican"),
    LANGUAGE_CR: _("Cree"),
    LANGUAGE_DV: _("Divehi"),
    LANGUAGE_DZ: _("Dzongkha"),
    LANGUAGE_EO: _("Esperanto"),
    LANGUAGE_ET: _("Estonian"),
    LANGUAGE_EE: _("Ewe"),
    LANGUAGE_FO: _("Faroese"),
    LANGUAGE_FJ: _("Fijian"),
    LANGUAGE_FF: _("Fulah"),
    LANGUAGE_GL: _("Galician"),
    LANGUAGE_GU: _("Gujarati"),
    LANGUAGE_HT: _("Haitian"),
    LANGUAGE_HZ: _("Herero"),
    LANGUAGE_HO: _("Hiri Motu"),
    LANGUAGE_IA: _("Interlingua"),
    LANGUAGE_IE: _("Interlingue"),
    LANGUAGE_IG: _("Igbo"),
    LANGUAGE_IK: _("Inupiaq"),
    LANGUAGE_IO: _("Ido"),
    LANGUAGE_IS: _("Icelandic"),
    LANGUAGE_IU: _("Inuktitut"),
    LANGUAGE_JV: _("Javanese"),
    LANGUAGE_KL: _("Kalaallisut"),
    LANGUAGE_KN: _("Kannada"),
    LANGUAGE_KR: _("Kanuri"),
    LANGUAGE_KS: _("Kashmiri"),
    LANGUAGE_KM: _("Central Khmer"),
    LANGUAGE_KI: _("Kikuyu"),
    LANGUAGE_RW: _("Kinyarwanda"),
    LANGUAGE_KV: _("Komi"),
    LANGUAGE_KG: _("Kongo"),
    LANGUAGE_KO: _("Korean"),
    LANGUAGE_KU: _("Kurdish"),
    LANGUAGE_KJ: _("Kuanyama"),
    LANGUAGE_LA: _("Latin"),
    LANGUAGE_LB: _("Luxembourgish"),
    LANGUAGE_LG: _("Ganda"),
    LANGUAGE_LI: _("Limburgan"),
    LANGUAGE_LN: _("Lingala"),
    LANGUAGE_LO: _("Lao"),
    LANGUAGE_LT: _("Lithuanian"),
    LANGUAGE_LU: _("Luba-Katanga"),
    LANGUAGE_LV: _("Latvian"),
    LANGUAGE_GV: _("Manx"),
    LANGUAGE_MG: _("Malagasy"),
    LANGUAGE_MS: _("Malay"),
    LANGUAGE_ML: _("Malayalam"),
    LANGUAGE_MT: _("Maltese"),
    LANGUAGE_MI: _("Maori"),
    LANGUAGE_MR: _("Marathi"),
    LANGUAGE_MH: _("Marshallese"),
    LANGUAGE_NA: _("Nauru"),
    LANGUAGE_NV: _("Navajo"),
    LANGUAGE_ND: _("North Ndebele"),
    LANGUAGE_NE: _("Nepali"),
    LANGUAGE_NG: _("Ndonga"),
    LANGUAGE_NN: _("Norwegian Nynorsk"),
    LANGUAGE_NO: _("Norwegian"),
    LANGUAGE_II: _("Sichuan Yi"),
    LANGUAGE_NR: _("South Ndebele"),
    LANGUAGE_OC: _("Occitan"),
    LANGUAGE_OJ: _("Ojibwa"),
    LANGUAGE_CU: _("Church Slavic"),
    LANGUAGE_OM: _("Oromo"),
    LANGUAGE_OR: _("Oriya"),
    LANGUAGE_OS: _("Ossetian"),
    LANGUAGE_PA: _("Punjabi"),
    LANGUAGE_PI: _("Pali"),
    LANGUAGE_PS: _("Pashto"),
    LANGUAGE_QU: _("Quechua"),
    LANGUAGE_RM: _("Romansh"),
    LANGUAGE_RN: _("Rundi"),
    LANGUAGE_SA: _("Sanskrit"),
    LANGUAGE_SC: _("Sardinian"),
    LANGUAGE_SD: _("Sindhi"),
    LANGUAGE_SE: _("Northern Sami"),
    LANGUAGE_SM: _("Samoan"),
    LANGUAGE_SG: _("Sango"),
    LANGUAGE_GD: _("Gaelic"),
    LANGUAGE_SN: _("Shona"),
    LANGUAGE_SK: _("Slovak"),
    LANGUAGE_SL: _("Slovenian"),
    LANGUAGE_SO: _("Somali"),
    LANGUAGE_ST: _("Southern Sotho"),
    LANGUAGE_SU: _("Sundanese"),
    LANGUAGE_SS: _("Swati"),
    LANGUAGE_TA: _("Tamil"),
    LANGUAGE_TG: _("Tajik"),
    LANGUAGE_TI: _("Tigrinya"),
    LANGUAGE_BO: _("Tibetan"),
    LANGUAGE_TK: _("Turkmen"),
    LANGUAGE_TL: _("Tagalog"),
    LANGUAGE_TN: _("Tswana"),
    LANGUAGE_TO: _("Tonga"),
    LANGUAGE_TW: _("Twi"),
    LANGUAGE_TY: _("Tahitian"),
    LANGUAGE_UG: _("Uighur"),
    LANGUAGE_VE: _("Venda"),
    LANGUAGE_VO: _("Volapük"),
    LANGUAGE_WA: _("Walloon"),
    LANGUAGE_CY: _("Welsh"),
    LANGUAGE_WO: _("Wolof"),
    LANGUAGE_FY: _("Western Frisian"),
    LANGUAGE_XH: _("Xhosa"),
    LANGUAGE_YI: _("Yiddish"),
    LANGUAGE_YO: _("Yoruba"),
    LANGUAGE_ZA: _("Zhuang"),
    LANGUAGE_ZU: _("Zulu"),
}

LANGUAGE_CHOICES = [
    (l, VERBOSE_LANGUAGES.get(l, l)) for l in settings.SUPPORTED_LANGUAGES
]


def is_valid_language(value):  # pragma: no cover
    return value in settings.SUPPORTED_LANGUAGES.keys()


def validate_language(value):  # pragma: no cover
    if not is_valid_language(value):
        raise ValidationError(_("{} is not a supported language.").format(value))
