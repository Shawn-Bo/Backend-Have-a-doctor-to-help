import pandas as pd
import torch

pd.options.display.float_format = '{:.5f}'.format
import pytorch_lightning as pl
from transformers import AdamW
from transformers.models.mt5.modeling_mt5 import MT5ForConditionalGeneration
import config_kgqt as config
from kgqa.utils import T5PegasusTokenizer

MODEL_NAME = config.MODEL_NAME
MODEL_BASE = config.MODEL_BASE
DEVICE = config.DEVICE

tokenizer = T5PegasusTokenizer.from_pretrained(
    MODEL_NAME,
    model_max_length=64,
    cache_dir=f"{MODEL_BASE}/{MODEL_NAME}")

tokenizer.add_tokens(["【事实提问】", "【问题解析】", "【-】", "【?】"])


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

    def training_step(self, batch, batch_idx):
        input_ids = batch["input_ids"]
        attention_mask = batch["attention_mask"]
        labels = batch["labels"]
        loss, outputs = self(input_ids, attention_mask, labels)
        self.log("train_loss", loss, prog_bar=True, logger=True)
        return loss

    def test_step(self, batch, batch_idx):
        input_ids = batch["input_ids"]
        attention_mask = batch["attention_mask"]
        labels = batch["labels"]
        loss, outputs = self(input_ids, attention_mask, labels)
        self.log("test_loss", loss, prog_bar=True, logger=True)
        return loss

    def validation_step(self, batch, batch_idx):
        input_ids = batch["input_ids"]
        attention_mask = batch["attention_mask"]
        labels = batch["labels"]
        loss, outputs = self(input_ids, attention_mask, labels)
        self.log("val_loss", loss, prog_bar=True, logger=True)
        return loss

    def configure_optimizers(self):
        return AdamW(self.parameters(), lr=0.0001)


def nlq2tsq(nlq_list):
    source_encoding = tokenizer.batch_encode_plus(
        nlq_list,
        max_length=64,
        padding="max_length",
        truncation="only_second",
        return_attention_mask=True,
        add_special_tokens=True,
        return_tensors="pt"
    )

    source_encoding = source_encoding.to(DEVICE)

    generated_ids_list = trained_model.model.generate(
        input_ids=source_encoding["input_ids"],
        attention_mask=source_encoding["attention_mask"],
        num_beams=3,
        max_length=64,
        repetition_penalty=2.5,
        length_penalty=1.0,
        early_stopping=True,
        use_cache=True,
        num_return_sequences=1,
        # return_dict_in_generate=True
    )

    # 接下来，计算每个候选序列的概率
    result_token_ids_list = generated_ids_list.sequences

    tsq_list = [
        tokenizer.decode(result_token_ids, skip_special_tokens=True, clean_up_tokenization_spaces=True).replace(" ", "")
        for result_token_ids in result_token_ids_list]
    return tsq_list


trained_model = QGModel.load_from_checkpoint(config.CKPT_PATH)
trained_model.to(DEVICE)
trained_model.freeze()

if __name__ == "__main__":
    # 最终实现QA的预测！
    nlq_list = [
        "有哪些食物是得了心脏病不能吃的？",
        "得了新冠肺炎要怎么办？",
        "描述一下什么是百日咳？",
        "得了心脏病治愈的希望大吗？",
        "百日咳的治疗时长？"
    ]

    tsq_list = nlq2tsq(nlq_list)

    print(tsq_list)
