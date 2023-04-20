from flask import Flask
from flask import request
import config_kgta as config
from flask_cors import CORS
from model_kgta import tsq_answer
from services.kgta.model_kgta_graph import graph_query

server = Flask(__name__)
cors = CORS(server)


@server.route('/kgta', methods=['post'])
def kgta():
    """
        将 tsq 解析为 answer_list 并返回。
        首先调用图数据库查询，如果无法查询到结果，则使用模型批量获得结果。
    """
    raw_tsq = request.json.get("tsq")
    # 对于输入的 tsq_list 应该为每个回复各自形成答案。具体而言，不断增加变体查询符进行推理。
    tsq_list = [f"{query_index}【-】{raw_tsq}" for query_index in range(10)]
    answer_list_string = "".join(tsq_answer(tsq_list))
    end_index = answer_list_string.find("【-】【-】")
    has_end_point = (end_index != -1)
    if has_end_point:
        return {"answer_list": answer_list_string[:end_index + 3].strip("【-】").split("【-】")}
    else:
        return {"answer_list": answer_list_string.strip("【-】").split("【-】")}


@server.route('/kgta_graph', methods=['post'])
def kgta_graph():
    """
        将 tsq 解析为 answer_list 并返回。
        首先调用图数据库查询，如果无法查询到结果，则使用模型批量获得结果。
    """
    raw_tsq: str = request.json.get("tsq")
    # 对于输入的 tsq_list 应该为每个回复各自形成答案。具体而言，不断增加变体查询符进行推理。
    if raw_tsq.count("【-】") == 2:
        S, P, Q = raw_tsq.split("【-】")
    else:
        return {"answer_list": []}
    graph_query_list = graph_query.query_graph_SP(S, P)

    return {"answer_list": graph_query_list}


server.run(port=config.PORT, host=config.HOST)
