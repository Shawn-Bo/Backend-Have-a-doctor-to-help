"""
    从Neo4j数据库中搜索节点。
"""

import pandas as pd


class GraphQuery(object):
    def __init__(self):
        self.graph_triples = pd.read_csv("E:\LaBarn\datasets\Haveadoctortohelp\graph_triples.csv",
                                         names=["S", "P", "O"])

    def query_graph_SP(self, S, P):
        result_records = self.graph_triples[(self.graph_triples["S"] == S) & (self.graph_triples["P"] == P)]
        result_list = result_records["O"].drop_duplicates(keep=False).tolist()
        return result_list

graph_query = GraphQuery()

if __name__ == "__main__":

    ans = graph_query.query_graph_SP("盆腔积液", "忌吃")
    print(ans)
