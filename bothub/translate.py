import time
import requests
from django.conf import settings

# enforce quotas (https://cloud.google.com/translate/quotas) (very naive implementation)

quota_char = 0
quota_limit = 100000
quota_wait = 100


def translate(tdict, source_lang, language):
    s_tdict = {}
    for d in tdict:
        sdict = {d: tdict[d]}
        s_tdict[d] = translate_single(sdict, source_lang, language)
    return s_tdict


def translate_single(tdict, source_lang, language):
    global quota_char
    # dont translate source language
    if language == source_lang:
        return tdict

    keys = sorted(tdict.keys())
    o_text_list = []
    for key in keys:
        o_text_list.append(tdict[key])

    data = {
        "q": o_text_list,
        "target": language,
        "format": "html",
        "source": source_lang,
        "model": "nmt",
    }

    headers = {"Content-Type": "application/json; charset: utf-8"}

    if not settings.GOOGLE_API_TRANSLATION_KEY:
        raise Exception("GOOGLE_API_TRANSLATION_KEY credential has not been set")

    URL = f"https://translation.googleapis.com/language/translate/v2?key={settings.GOOGLE_API_TRANSLATION_KEY}"

    quota_char += len(str(data))
    if quota_char >= quota_limit:
        print("Would hit rate limit - waiting %s seconds" % (quota_wait + 5))
        time.sleep(quota_wait + 5)
        print("Resuming after rate limit")
        quota_char = 0

    print("  translating %s -> %s: %s" % (source_lang, language, keys))

    req = requests.post(URL, headers=headers, json=data)
    response = req.json()

    if (
        "error" in response
        and "code" in response["error"]
        and response["error"]["code"] == 403
    ):
        print("Rate limit hit - waiting %s seconds" % (quota_wait + 5))
        time.sleep(quota_wait + 5)
        quota_char = 0
        print("Resuming after rate limit")
        return translate_single(tdict, source_lang, language)

    cnt = 0
    for t in response["data"]["translations"]:
        tdict[keys[cnt]] = t["translatedText"]
        cnt += 1

    return tdict
