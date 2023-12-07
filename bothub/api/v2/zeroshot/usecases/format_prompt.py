
class FormatPrompt:
    const_prompt_data = {
        "pt-br": {
            "prompt_context": "Você é muito especialista em ",
            "prompt_has_classes": ". Você possui as classes:\n\n",
            "prompt_class_prefix": "Classe: ",
            "prompt_context_classes": "Contexto da classe ",
            "is_class_context_prefix": True,
            "prompt_none_name": "Nenhuma",
            "prompt_none_definition": "Classe: Nenhuma\nContexto da classe Nenhuma: A classe nenhuma é usada quando a frase não se relaciona com as outras classes definidas.\n\n",
            "prompt_phrase_prefix": "Frase: ",
            "prompt_analyse_text": "Pare, pense bem e analise qual é a melhor resposta de classe para a frase, responda só se você tiver muita certeza.\n\nClasse: "
        }, 
        "en": {
            "prompt_context": "You are very expert in ",
            "prompt_has_classes": ". You have the following classes:\n\n",
            "prompt_class_suffix": "Class: ",
            "is_class_context_prefix": False,
            "prompt_context_classes": " class context",
            "prompt_none_name": "None",
            "prompt_none_definition": "Class: None\n\nNone class context: Use when a sentence doesn't align with any of the classes above.\n",
            "prompt_phrase_prefix": "Sentence: ",
            "prompt_analyse_text": "Stop, think carefully and analyze what the best class answer to the sentence is, only answer if you are very sure.\n\nClass:"
        },
        "es": {
            "prompt_context": "Eres muy experto en ",
            "prompt_has_classes": ". Usted posee las clases:\n\n",
            "prompt_class_prefix": "Clase: ",
            "is_class_context_prefix": True,
            "prompt_context_classes": "Contexto de la clase ",
            "prompt_none_name": "Ninguna",
            "prompt_none_definition": "Clase: Ninguna\n\nContexto de la clase Ninguna: Aplicable si el tema no corresponde con las clases establecidas.",
            "prompt_phrase_prefix": "Frase: ",
            "prompt_analyse_text": "Detente, piensa detenidamente y analiza cuál es la mejor respuesta de clase a la frase, responde sólo si estás muy seguro.\n\nClase:"
        }
    }

    def generate_prompt(self, language: str, zeroshot_data: dict):
        translated_text = self.const_prompt_data[language]
        prompt = translated_text.get("prompt_context") + zeroshot_data.get("context") + translated_text.get("prompt_has_classes")
        for option in zeroshot_data.get("options"):
            prompt += translated_text.get("prompt_class_prefix") + option.get("class", "").capitalize() + "\n"
            if translated_text.get("is_class_context_prefix"):
                prompt += translated_text.get("prompt_context_classes") + option.get("class", "").capitalize() + ": "
            else:
                prompt += option.get("class", "").capitalize() + translated_text.get("prompt_context_classes") + ": "
            prompt += option.get("context") + "\n"
        prompt += translated_text.get("prompt_none_definition") + translated_text.get("prompt_phrase_prefix")
        prompt += zeroshot_data.get("text") + "\n" + translated_text.get("prompt_analyse_text")

        return prompt
    
    def get_none_class(self, language: str):
        data = self.const_prompt_data.get(language)
        return data.get("prompt_none_name", "Nenhuma")
