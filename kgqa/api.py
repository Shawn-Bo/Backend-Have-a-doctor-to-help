import textwrap

import openai
import requests

from kgqa.utils import chatgpt_query


def get_response(session_json: dict):
    nlq: str = session_json["session_messages"][-1]["message_text"]
    # 我们先做三元组的查询，用本地的模型解决问题
    response_text = e2e_kgqa(nlq)  # 从三元组开始 端到端的问答

    session_json["session_messages"].append({
        "message_id": len(session_json['session_messages']),
        "message_sender": "robot",
        "message_time": "",  # 即刻响应，不需要知道时间。
        "message_text": response_text
    })
    return session_json


def e2e_kgqa(nlq, ag=True):
    # qt
    nlq_list = [nlq]
    qt_url = f"http://127.0.0.1:9000/kgqt"
    tsq = requests.post(
        url=qt_url,
        json={"nlq_list": nlq_list}
    ).json()["tsq_list"][0]
    # ta
    ta_url = f"http://127.0.0.1:9001/kgta"
    answer_list = requests.post(
        url=ta_url,
        json={"tsq": tsq}
    ).json()["answer_list"]
    # ta_graph
    ta_graph_url = f"http://127.0.0.1:9001/kgta_graph"
    answer_graph_list = requests.post(
        url=ta_graph_url,
        json={"tsq": tsq}
    ).json()["answer_list"]

    response_dict = {
        "answer_list": answer_list,
        "answer_graph_list": answer_graph_list
    }

    if ag:  # 目前还不知道要怎么做

        response_str = chatgpt_query(textwrap.dedent(f"""
            接下来，你需要扮演一名医生，根据给定的信息，回答患者的问题。
            患者的问题是：{nlq},
            已知信息：
                1. 通过问题解析，将患者的问题转为三元组查询：{tsq}
                2. 从知识图谱数据库查询此问题，得到结果：{answer_list}
                3. 从医疗问答语言模型中推理问题，得到结果：{answer_graph_list}
            下面是你的回答：
        """))

        return {"tsq": tsq,
                "answer_list": answer_list,
                "answer_graph_list": answer_graph_list,
                "response_str": response_str}

    else:
        return {"tsq": tsq,
                "answer_list": response_dict}


if __name__ == "__main__":
    al = e2e_kgqa("得了心脏病如何治疗？")
    print(al)
