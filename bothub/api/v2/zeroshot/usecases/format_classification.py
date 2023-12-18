import unicodedata

from .format_prompt import FormatPrompt


class FormatClassification:
    def __init__(self, classification_data):
        self.classification_data = classification_data

    def _get_normalize_text(self, text):
        return unicodedata.normalize('NFKD', text).encode('ASCII', 'ignore').decode('utf-8')

    def _get_classification(self):
        class_answer = ""
        classification_text = self._get_normalize_text(self.classification_data.get("text")[0].strip().lower())
        for ch in classification_text:
            if ord(ch) >= ord('a') and ord(ch) <= ord('z') :
                class_answer += ch
            else:
                break
        return class_answer

    def get_classify(self, options, language):
        classification = self._get_classification()
        formatter = FormatPrompt()
        classify = {"other": False, "classification": ""}
        for option in options:
            option_class = self._get_normalize_text(option.get("class").strip().lower())
            if classification == option_class:
                classify["classification"] = option.get("class")
                break
        if len(classify["classification"]) == 0:
            classify["classification"] = formatter.get_none_class(language=language)
            classify["other"] = True
        return classify
