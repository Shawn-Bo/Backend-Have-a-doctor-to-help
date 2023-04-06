from neo4j import GraphDatabase

uri = "bolt://localhost:7687"

driver = GraphDatabase.driver(uri)

with driver.session() as session:
    results = session.run("""MATCH (n:疾病)
WITH n, rand() AS rand
RETURN n
ORDER BY rand
LIMIT 1""").single()
    results["n"]["名称"]
driver.close()
