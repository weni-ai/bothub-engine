import unicodedata
import re

from django.conf import settings
from .format_prompt import FormatPrompt


class FormatClassification:
    const_none_class_id = -1
    const_none_class = "None"

    def __init__(self, classification_data: dict):
        self.model_backend = settings.ZEROSHOT_MODEL_BACKEND
        self.classification_data = classification_data

    def get_classification(self, zeroshot_data):
        if self.model_backend == "runpod":
            return self._get_runpod_classification(zeroshot_data)
        elif self.model_backend == "bedrock":
            return self._get_bedrock_classification(zeroshot_data)
        else:
            raise ValueError(f"Unsupported model backend: {self.model_backend}")

    def _get_data_none_class(self):
        return self.const_none_class

    def _get_number_from_output(self, output):
        output_result = self.const_none_class_id
        match = re.search(r'-?\d+', output)
        if match:
            output_result = match.group()

        return output_result

    def _get_formatted_output(self, output_text, zeroshot_data):
        classification = {"other": True, "classification": self._get_data_none_class()}
        response_text = output_text if output_text else self._get_data_none_class()

        response_prepared = response_text.lower()
        response_prepared = response_text.strip().strip(".").strip("\n").strip("'")

        output = self._get_number_from_output(response_prepared)

        if output or output != self.const_none_class_id:
            all_classes = zeroshot_data.get("options")
            for class_obj in all_classes:
                if output == str(class_obj.get("id")):
                    classification["other"] = False
                    classification["classification"] = class_obj.get("class")
                    break

        return classification

    def _get_runpod_classification(self, zeroshot_data):
        output_text = self.classification_data.get("output")[0].get("choices")[0].get("tokens")[0]
        return self._get_formatted_output(output_text, zeroshot_data)

    def _get_bedrock_classification(self, zeroshot_data):
        output_text = self.classification_data.get("outputs")[0].get("text").strip()
        return self._get_formatted_output(output_text, zeroshot_data)
