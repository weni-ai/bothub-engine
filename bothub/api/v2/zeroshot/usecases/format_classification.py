from .format_prompt import FormatPrompt

class FormatClassification:
    def __init__(self, classification_data):
        self.classification_data = classification_data
    
    def get_classify(self, options, language):
        classification = self.classification_data.get("text")[0].strip().lower()
        formatter = FormatPrompt()
        classify = {"other": False, "classification": ""}
        for option in options:
            option_class = option.get("class").strip().lower()
            if classification == option_class:
                classify["classification"] = option.get("class")
                break
        if len(classify["classification"]) == 0:
            classify["classification"] = formatter.get_none_class(language=language)
            classify["other"] = True
        return classify
