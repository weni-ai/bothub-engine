from transformers import GPT2TokenizerFast
import re

from django.conf import settings
from typing import Tuple, List


class ChatGPTTokenText:
    max_tokens: int = settings.GPT_MAX_TOKENS

    def count_tokens(self, text: str) -> Tuple[int, List[str]]:
        tokenizer = GPT2TokenizerFast.from_pretrained("gpt2")

        sentence_boundary_pattern = r'(?<=[.!?])\s+(?=[^\d])'
        sentence_boundaries = [(m.start(), m.end()) for m in re.finditer(sentence_boundary_pattern, text)]

        chunks = []
        current_chunk = []
        current_token_count = 0
        current_position = 0
        total_token_count = 0

        for boundary_start, boundary_end in sentence_boundaries:
            sentence = text[current_position : boundary_start + 1]
            current_position = boundary_end

            token_count = len(tokenizer(sentence)["input_ids"])
            total_token_count += token_count

            if current_token_count + token_count <= self.max_tokens:
                current_chunk.append(sentence)
                current_token_count += token_count
            else:
                chunks.append(''.join(current_chunk))
                current_chunk = [sentence]
                current_token_count = token_count

        return (total_token_count, chunks)
