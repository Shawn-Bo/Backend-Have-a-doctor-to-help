import torch

PORT = 9000
HOST = "0.0.0.0"
MODEL_NAME = "imxly/t5-pegasus-small"
MODEL_BASE = "E:/LaBarn/checkpoints"
DEVICE = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
CKPT_PATH = f"{MODEL_BASE}/KBQGT5/KGQT.ckpt"
