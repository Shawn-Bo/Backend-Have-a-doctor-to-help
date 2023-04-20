import requests
import test_config_kgta as config

tsq = "盆腔积液【-】宜吃【-】【?】"
url = f"http://{config.SERVE_HOST}:{config.PORT}/kgta_graph"
ans = requests.post(
    url=url,
    json={"tsq": tsq}
)

print(ans.json())
