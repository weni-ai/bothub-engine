import time
import requests
from django.conf import settings

# enforce quotas (https://cloud.google.com/translate/quotas) (very naive implementation)

quota_char = 0
quota_limit = 100000
quota_wait = 100


def translate(text, source_lang, target_language):
    global quota_char
    # dont translate source language
    if target_language == source_lang:
        return text

    data = {
        "q": text,
        "target": target_language,
        "format": "text",
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
        return translate(text, source_lang, target_language)

    return response.get("data").get("translations")[0].get("translatedText")
