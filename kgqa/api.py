import openai
from kgqa.qa import predict
# Set your API key
openai.api_key = "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"


def get_response(session_json: dict):
    raw_query_text: str = session_json["session_messages"][-1]["message_text"]
    # 我们先做三元组的查询，用本地的模型解决问题
    tri_query_text = generate_kgqt([f"【问题解析】{raw_query_text}"])[6:]  # 从三元组开始
    # 然后调用api

    print("解析后的问题三元组：", tri_query_text)
    tri_response_text = predict(tri_query_text, raw_query_text)
    print("响应的知识：", tri_response_text)
    context_text =[session_json["session_messages"][i]["message_text"] for i in range(len(session_json["session_messages"]))]
    response_text = fine_tune_response(f"之前的所有提问：{context_text}\n最后一次提问：{raw_query_text}。经过诊断可能相关的答案（注意这些内容患者没有说过也没有听过）：{tri_response_text}。")  # 省着点用


    session_json["session_messages"].append({
        "message_id": len(session_json['session_messages']),
        "message_sender": "robot",
        "message_time": "",  # 即刻响应，不需要知道时间。
        "message_text": response_text
    })
    return session_json


def fine_tune_response(raw_text: str):
    # Use the chatGPT model
    completion = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{
            "role": "user",
            "content": f"""现在你扮演一名医生，根据提供的信息回答患者的问题，并给予必要的支持和鼓励。注意，尽可能忠于提供的信息，可以对结果进行补充，但是不能曲解原意。提供的情报中有些信息可能无效，请忽略它们。用"您好"开始，婉拒问诊不相关的对话。{raw_text}"""
        }]
    )

    # Get the generated text
    return completion["choices"][0]["message"]["content"]  # 将最好的答案作为结果返回
