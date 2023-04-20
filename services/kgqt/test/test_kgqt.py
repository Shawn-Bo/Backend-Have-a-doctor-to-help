import requests
import test_config_kgqt as config

nlq_list = [
    "新冠肺炎患者应该避免摄入哪些食物？",
    "你知道电视剧《花千骨》中，新冠肺炎患者有哪些饮食注意事项吗？",
    "请问新冠肺炎患者应该吃什么药？",
    "有哪些食物是得了新冠肺炎不能吃的？",
    "得了新冠肺炎要怎么治疗效果好？",
    "描述一下什么是新冠肺炎？",
    "新冠肺炎症状？",
    "得了新冠肺炎有多大的概率能治好？",
    "你们好，我是杰哥。请问新冠肺炎应该去哪个科室就诊？",
    "新冠肺炎推荐吃什么药物？",
    "什么人群易感新冠肺炎呢？"
]
url = f"http://{config.SERVE_HOST}:{config.PORT}/kgqt"
ans = requests.post(
    url=url,
    json={"nlq_list": nlq_list}
)

print(ans.json())
