import unicodedata
import re

from .format_prompt import FormatPrompt


class FormatClassification:
    const_none_class_id = -1
    const_none_class = {"por": "Nenhuma", "eng": "None", "spa": "Ninguna"}

    def __init__(self, language: str, classification_data: dict):
        self.language = language
        self.classification_data = classification_data

    def _get_data_none_class(self):
        return self.const_none_class[self.language]

    def _get_number_from_output(self, output):
        output_result = self.const_none_class_id
        match = re.search(r'-?\d+', output)
        if match:
            output_result = match.group()

        return output_result

    def _get_final_output(self):
        output_text = self.classification_data.get("output").get("text")
        response_text = output_text[0] if output_text else self._get_data_none_class()

        response_prepared = response_text.lower()
        response_prepared = response_text.strip().strip(".").strip("\n").strip("'")

        output = self._get_number_from_output(response_prepared)
        return output


    def get_classify(self, zeroshot_data):
        classify = {"other": True, "classification": self._get_data_none_class()}
        output = self._get_final_output()

        if output or output != self.const_none_class_id:
            all_classes = zeroshot_data.get("options")
            for class_obj in all_classes:
                if output == str(class_obj.get("id")):
                    classify["other"] = False
                    classify["classification"] = class_obj.get("class")
                    break

        return classify
