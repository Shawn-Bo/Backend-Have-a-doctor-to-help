import requests
import test_config_kgta as config

tsq = "新冠肺炎【-】治愈概率【-】【?】"
url = f"http://{config.SERVE_HOST}:{config.PORT}/kgqt"
ans = requests.post(
    url=url,
    json={"tsq": tsq}
)

print(ans.json())
