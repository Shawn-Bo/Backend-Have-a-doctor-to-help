import pandas as pd
pd.options.display.float_format = '{:.5f}'.format
import pytorch_lightning as pl
from transformers import AdamW
from transformers.models.mt5.modeling_mt5 import MT5ForConditionalGeneration
import torch
from kgqa.utils import T5PegasusTokenizer

device = 'cuda' if torch.cuda.is_available() else 'cpu'

MODEL_NAME = "imxly/t5-pegasus-small"
MODEL_BASE = "E:/LaBarn/checkpoints"

tokenizer = T5PegasusTokenizer.from_pretrained(
    MODEL_NAME,
    model_max_length=64,
    cache_dir=f"{MODEL_BASE}/{MODEL_NAME}")

tokenizer.add_tokens(["【恢复问句】", "[MSK]", "【恢复问诊】,【恢复诊断】", "【事实提问】", "【-】", "【问题解析】", "【?】"])


class QGModel(pl.LightningModule):
    def __init__(self):
        super().__init__()
        self.model = MT5ForConditionalGeneration.from_pretrained(
            MODEL_NAME,
            cache_dir=f"{MODEL_BASE}/{MODEL_NAME}",
            return_dict=True)
        self.model.resize_token_embeddings(len(tokenizer))

    def forward(self, input_ids, attention_mask, labels=None):
        output = self.model(
            input_ids=input_ids,
            attention_mask=attention_mask,
            labels=labels
        )
        return output.loss, output.logits


def generate_answer(questions):
    source_encoding = tokenizer.batch_encode_plus(
        questions,
        max_length=64,
        padding="max_length",
        truncation="only_second",
        return_attention_mask=True,
        add_special_tokens=True,
        return_tensors="pt"
    )

    generated_ids_list = trained_model.model.generate(
        input_ids=source_encoding["input_ids"],
        attention_mask=source_encoding["attention_mask"],
        num_beams=3,
        max_length=64,
        early_stopping=True,
        use_cache=True,
        # do_sample=True, 当do_sample为True时，会对每个生成步骤进行采样，即从softmax分布中随机采样一个token作为下一个生成的token。
        num_return_sequences=1,
        output_scores=True,
        return_dict_in_generate=True
    )
    # 接下来，计算每个候选序列的概率
    result_token_ids = generated_ids_list.sequences
    result_sequences_scores = torch.exp(generated_ids_list.sequences_scores)
    conclusions = []
    for return_sequence_index in range(result_token_ids.shape[0]):
        return_sequence = result_token_ids[return_sequence_index]  # 目前是(64个int组成的列表)
        # 差不多了就输出结果吧
        conclusions.append([
            tokenizer.decode(return_sequence, skip_special_tokens=True, clean_up_tokenization_spaces=True),
            float(result_sequences_scores[return_sequence_index].numpy())
        ])
    return conclusions


def predict(query, raw_query,num=10) -> str:
    # 用 num 控制查询枚举的结果数
    qs = [f"{i}【-】{query}" for i in range(num)]
    # 批量推理并排序分数
    conclusions = pd.DataFrame(generate_answer(qs), columns=["答案", "分数"]).sort_values("分数", ascending=False)
    # 清理查询结果
    conclusions = conclusions.drop_duplicates(subset=["答案"]).reset_index(drop=True)["答案"].to_list()
    # 选取靠前的结果
    conclusions = conclusions
    result = f"问题：{raw_query}？即：{query}已知：" + ", ".join(conclusions)
    return result


trained_model = QGModel.load_from_checkpoint(f"./kgqa/last.ckpt")
trained_model.freeze()

