from functools import partial

import jieba
from transformers import BertTokenizer


class T5PegasusTokenizer(BertTokenizer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.pre_tokenizer = partial(jieba.cut, HMM=False)

    def _tokenize(self, text, *arg, **kwargs):
        split_tokens = []
        for text in self.pre_tokenizer(text):
            if text in self.vocab:
                split_tokens.append(text)
            else:
                split_tokens.extend(super()._tokenize(text))
        return split_tokens


def init_T5PegasusTokenizer(MODEL_NAME, MODEL_BASE):
    tokenizer = T5PegasusTokenizer.from_pretrained(
        MODEL_NAME,
        model_max_length=64,
        cache_dir=f"{MODEL_BASE}/{MODEL_NAME}")

    tokenizer.add_tokens(["【事实提问】", "【问题解析】", "【-】", "【?】"])
    return tokenizer


import openai


def chatgpt_query(prompt):
    # openai.api_key = "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"  # 这个是我的

    openai.api_key = "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"  # 这个是18美元 9.9元买的
    # openai.api_key = "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"

    completion = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}]
    )
    return completion["choices"][0]["message"]["content"]
