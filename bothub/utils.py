from collections import OrderedDict


def cast_supported_languages(i):
    return OrderedDict([
        x.split(':', 1) if ':' in x else (x, x) for x in
        i.split('|')
    ])


def cast_empty_str_to_none(value):
    return value or None
