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
