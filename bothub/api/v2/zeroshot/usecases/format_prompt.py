BASE_PROMPT = """<s>[INST] {context_description} {context}
{reflection}

# {classes_title}
{all_classes}

# {sentence_title} {input}
# {class_id_title} [/INST]"""

class FormatPrompt:
    const_prompt_data = {
        "por": {
            "context_description": "Você é muito especialista em classificar a frase do usuário em um chatbot sobre:",
            "reflection": "Pare, pense bem e responda com APENAS UM ÚNICO `id` da classe que melhor represente a intenção para a frase do usuário de acordo com a análise de seu contexto, responda APENAS com o `id` da classe só se você tiver muita certeza e não explique o motivo. Na ausência, falta de informações ou caso a frase do usuário não se enquadre em nenhuma classe, classifique como \"-1\".",
            "classes_title": "Essas são as Classes com seus Id e Contexto:",
            "sentence_title": "Frase do usuário:",
            "class_id_title": "Id da Classe:"
        }, 
        "eng": {
            "context_description": "You are very expert in classifying the user sentence in a chatbot about:",
            "reflection": "Stop, think carefully, and respond with ONLY ONE SINGLE `id` of the class that best represents the intention for the user's sentence according to the analysis of its context, respond ONLY with the `id` of the class if you are very sure and do not explain the reason. In the absence, lack of information, or if the user's sentence does not fit into any class, classify as \"-1\".",
            "classes_title": "These are the Classes and its Context:",
            "sentence_title": "User's sentence:",
            "class_id_title": "Class Id:"
        },
        "spa": {
            "context_description": "Eres muy experto en clasificar la frase del usuario en un chatbot sobre:",
            "reflection": "Deténgase, piense bien y responda con SOLO UN ÚNICO `id` de la clase que mejor represente la intención para la frase del usuario de acuerdo con el análisis de su contexto, responda SOLO con el `id` de la clase si está muy seguro y no explique el motivo. En ausencia, falta de información o en caso de que la frase del usuario no se ajuste a ninguna clase, clasifique como \"-1\".",
            "classes_title": "Estas son las Clases con sus Id y Contexto:",
            "sentence_title": "Frase del usuario:",
            "class_id_title": "Id de la Clase:"
        }
    }

    def generate_prompt(self, zeroshot_data: dict):
        language = zeroshot_data.get("language", self.get_default_language())
        translated_text = self.const_prompt_data[language]
        context = zeroshot_data.get("context")
        input = zeroshot_data.get("text")
        all_classes = self.setup_ids_on_classes(zeroshot_data.get("options"))

        prompt = BASE_PROMPT.format(context_description=translated_text.get("context_description"),
                                    reflection=translated_text.get("reflection"),
                                    classes_title=translated_text.get("classes_title"),
                                    sentence_title=translated_text.get("sentence_title"),
                                    class_id_title=translated_text.get("class_id_title"),
                                    context=context,
                                    all_classes=all_classes,
                                    input=input)

        return prompt
    
    def setup_ids_on_classes(self, all_classes):
        for index, class_obj in enumerate(all_classes):
            id = index + 1
            class_obj["id"] = id

        return all_classes

    def get_default_language(self):
        return "por"
