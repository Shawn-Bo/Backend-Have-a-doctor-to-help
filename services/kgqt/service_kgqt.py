from flask import Flask
from flask import request
import config_kgqt as config
from flask_cors import CORS
from model_kgqt import nlq2tsq

server = Flask(__name__)
cors = CORS(server)


@server.route('/kgqt', methods=['post'])
def kgqt():
    """
        将 nlq_list 解析为 tsq_list 并返回。
    :return:
    """
    nlq_list = request.json.get("nlq_list")
    tsq_list = nlq2tsq(nlq_list)
    return {"tsq_list": tsq_list}


server.run(port=config.PORT, host=config.HOST)
