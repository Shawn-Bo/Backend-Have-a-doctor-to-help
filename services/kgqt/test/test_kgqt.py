import requests
import test_config_kgqt as config

nlq_list = [
    "有哪些食物是得了心脏病不能吃的？"
]
url = f"http://{config.SERVE_HOST}:{config.PORT}/kgqt"
print(url)
ans = requests.post(
    url=url,
    json={"nlq_list": nlq_list}
)

print(ans.json())
