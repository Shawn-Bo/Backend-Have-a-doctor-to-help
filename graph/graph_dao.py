"""
    从Neo4j数据库中搜索节点。
"""
from neo4j import GraphDatabase


class GraphDao(object):
    def __init__(self, uri):
        self.driver = GraphDatabase.driver(uri)

    def close(self):
        self.driver.close()

    def query_random_entity_name(self):
        """
        :return: 随机一个疾病的实体名称
        """
        with self.driver.session() as session:
            result = session.run("""MATCH (n:疾病) WITH n, rand() AS rand
        RETURN n ORDER BY rand LIMIT 1""").single()
        return result["n"]["名称"]

    def query_entity_by_name(self, entity_name, triple_limit=5):
        """
        :param entity_name: 查询的实体名
        :return:
            一个列表，既有属性三元组，又有关系三元组
        """
        triples = []
        with self.driver.session() as session:
            results_head = session.run(
                f"""MATCH (n {{名称: '{entity_name}'}})-[r]->(m) RETURN n, r, m LIMIT {triple_limit}"""
            )
            results_tail = session.run(
                f"""MATCH (n)-[r]->(m {{名称: '{entity_name}'}}) RETURN n, r, m LIMIT {triple_limit}"""
            )
            query_records = [record for record in results_head] + [record for record in results_tail]
        if len(query_records) == 0:
            return {"code": "success", "data": []}
        EAV_triples = [[entity_name, *item] for item in query_records[0][0].items()]
        triples.extend(EAV_triples)
        SPO_triples = [[query_record.values()[index]["名称"] for index in range(3)] for query_record in query_records]
        triples.extend(SPO_triples)

        filtered_triples = [[a, b, c] for [a, b, c] in triples
                            if b != '名称' and len(c) <= 16]
        print(filtered_triples)

        return {"code": "success", "query_entity": entity_name, "data": filtered_triples}


graph_dao = GraphDao("bolt://localhost:7687")

if __name__ == "__main__":
    entity_name = graph_dao.query_random_entity_name()
    print(entity_name)
    rs = graph_dao.query_entity_by_name(entity_name)
    print(rs)
    graph_dao.close()
