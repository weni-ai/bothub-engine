BASE_PROMPT = """<|begin_of_text|><|start_header_id|>system<|end_header_id|>

{system_prompt}<|eot_id|><|start_header_id|>user<|end_header_id|>

{input}<|eot_id|><|start_header_id|>assistant<|end_header_id|>

"""

class FormatPrompt:
    const_prompt_data = {
        "system_prompt": "Task: Classify the 'User' message within a chatbot about: {context}. Carefully consider the context and respond with ONLY ONE tag of the class that best represents the intent of the 'User' message with the below categories.\n\n<BEGIN CONTENT CATEGORIES>\n{classes_formatted}\n<END CONTENT CATEGORIES>",
        "question": "{input}",
    }

    def generate_prompt(self, language: str, zeroshot_data: dict):
        context = zeroshot_data.get("context")
        input = zeroshot_data.get("text")
        all_classes = self.setup_ids_on_classes(zeroshot_data.get("options"))
        classes_formatted = self.format_classes(all_classes)

        system_prompt = self.const_prompt_data["system_prompt"].format(context=context, classes_formatted=classes_formatted)
        question = self.const_prompt_data["question"].format(input=input)

        prompt = BASE_PROMPT.format(system_prompt=system_prompt, input=question)
        return prompt
    
    def setup_ids_on_classes(self, all_classes):
        for index, class_obj in enumerate(all_classes):
            id = index + 1
            class_obj["id"] = id
        return all_classes

    def format_classes(self, all_classes):
        classes_formatted = '\n'.join([f"A{mclass['id']}: {mclass['class']} - {mclass['context']}" for index, mclass in enumerate(all_classes)])
        classes_formatted += f"\nA{len(all_classes)+1}: none - if there is insufficient information or if the User message doesn't fit any class"
        return classes_formatted

    def get_default_language(self):
        return "por"