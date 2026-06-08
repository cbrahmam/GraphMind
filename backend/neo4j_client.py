from neo4j import GraphDatabase
from backend.config import NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD


class Neo4jClient:
    _instance = None
    _driver = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def connect(self):
        if self._driver is None:
            self._driver = GraphDatabase.driver(
                NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD)
            )
            self._driver.verify_connectivity()

    def close(self):
        if self._driver:
            self._driver.close()
            self._driver = None

    @property
    def driver(self):
        if self._driver is None:
            self.connect()
        return self._driver

    def run_query(self, cypher: str, params: dict | None = None) -> list[dict]:
        with self.driver.session() as session:
            result = session.run(cypher, params or {})
            return [record.data() for record in result]

    def create_node(self, label: str, properties: dict) -> str:
        cypher = (
            f"CREATE (n:{label} $props) "
            "SET n.id = randomUUID() "
            "RETURN n.id AS id"
        )
        records = self.run_query(cypher, {"props": properties})
        return records[0]["id"]

    def merge_node(self, label: str, name: str, properties: dict) -> str:
        cypher = (
            f"MERGE (n:{label} {{name: $name}}) "
            "ON CREATE SET n += $props, n.id = randomUUID() "
            "ON MATCH SET n += $props "
            "RETURN n.id AS id"
        )
        records = self.run_query(cypher, {"name": name, "props": properties})
        return records[0]["id"]

    def create_relationship(
        self,
        from_name: str,
        from_label: str,
        to_name: str,
        to_label: str,
        rel_type: str,
        properties: dict | None = None,
    ):
        cypher = (
            f"MATCH (a:{from_label} {{name: $from_name}}) "
            f"MATCH (b:{to_label} {{name: $to_name}}) "
            f"MERGE (a)-[r:{rel_type}]->(b) "
            "SET r += $props "
            "RETURN type(r) AS type"
        )
        self.run_query(
            cypher,
            {
                "from_name": from_name,
                "to_name": to_name,
                "props": properties or {},
            },
        )

    def get_node(self, node_id: str) -> dict | None:
        records = self.run_query(
            "MATCH (n {id: $id}) RETURN n, labels(n) AS labels",
            {"id": node_id},
        )
        if not records:
            return None
        node = dict(records[0]["n"])
        node["labels"] = records[0]["labels"]
        return node

    def get_node_with_relationships(self, node_id: str) -> dict | None:
        node = self.get_node(node_id)
        if not node:
            return None
        rels = self.run_query(
            """MATCH (n {id: $id})-[r]-(m)
               RETURN type(r) AS type, properties(r) AS props,
                      m.name AS target_name, labels(m) AS target_labels,
                      m.id AS target_id,
                      startNode(r) = n AS outgoing""",
            {"id": node_id},
        )
        node["relationships"] = rels
        return node

    def search_nodes(
        self, label: str | None = None, search: str = ""
    ) -> list[dict]:
        if label:
            cypher = (
                f"MATCH (n:{label}) "
                "WHERE toLower(n.name) CONTAINS toLower($search) "
                "RETURN n, labels(n) AS labels "
                "LIMIT 25"
            )
        else:
            cypher = (
                "MATCH (n) "
                "WHERE toLower(n.name) CONTAINS toLower($search) "
                "RETURN n, labels(n) AS labels "
                "LIMIT 25"
            )
        records = self.run_query(cypher, {"search": search})
        results = []
        for rec in records:
            node = dict(rec["n"])
            node["labels"] = rec["labels"]
            results.append(node)
        return results

    def get_neighbors(self, node_id: str, depth: int = 1) -> dict:
        cypher = (
            f"MATCH path = (n {{id: $id}})-[*1..{min(depth, 5)}]-(m) "
            "WITH nodes(path) AS ns, relationships(path) AS rs "
            "UNWIND ns AS node "
            "WITH collect(DISTINCT node) AS allNodes, rs "
            "UNWIND rs AS rel "
            "WITH allNodes, collect(DISTINCT rel) AS allRels "
            "RETURN allNodes, allRels"
        )
        records = self.run_query(cypher, {"id": node_id})
        if not records:
            return {"nodes": [], "links": []}

        nodes = []
        seen_ids = set()
        for node in records[0]["allNodes"]:
            props = dict(node)
            nid = props.get("id", props.get("name", ""))
            if nid not in seen_ids:
                seen_ids.add(nid)
                nodes.append(props)

        links = []
        for rel in records[0]["allRels"]:
            links.append(
                {
                    "source": dict(rel.start_node).get("id", ""),
                    "target": dict(rel.end_node).get("id", ""),
                    "type": rel.type,
                    "properties": dict(rel),
                }
            )
        return {"nodes": nodes, "links": links}

    def get_schema(self) -> dict:
        labels_result = self.run_query(
            "CALL db.labels() YIELD label RETURN collect(label) AS labels"
        )
        labels = labels_result[0]["labels"] if labels_result else []

        rel_types_result = self.run_query(
            "CALL db.relationshipTypes() YIELD relationshipType "
            "RETURN collect(relationshipType) AS types"
        )
        rel_types = rel_types_result[0]["types"] if rel_types_result else []

        label_details = []
        for label in labels:
            count_result = self.run_query(
                f"MATCH (n:{label}) RETURN count(n) AS count"
            )
            count = count_result[0]["count"] if count_result else 0

            props_result = self.run_query(
                f"MATCH (n:{label}) WITH n LIMIT 5 "
                "UNWIND keys(n) AS key "
                "RETURN collect(DISTINCT key) AS keys"
            )
            props = props_result[0]["keys"] if props_result else []
            label_details.append(
                {"label": label, "count": count, "property_keys": props}
            )

        rel_details = []
        for rt in rel_types:
            count_result = self.run_query(
                f"MATCH ()-[r:{rt}]->() RETURN count(r) AS count"
            )
            count = count_result[0]["count"] if count_result else 0
            rel_details.append({"type": rt, "count": count})

        return {
            "node_labels": label_details,
            "relationship_types": rel_details,
        }

    def get_stats(self) -> dict:
        node_count = self.run_query("MATCH (n) RETURN count(n) AS count")
        rel_count = self.run_query("MATCH ()-[r]->() RETURN count(r) AS count")

        label_counts = self.run_query(
            "MATCH (n) "
            "WITH labels(n) AS lbls "
            "UNWIND lbls AS lbl "
            "RETURN lbl AS label, count(*) AS count "
            "ORDER BY count DESC"
        )

        rel_type_counts = self.run_query(
            "MATCH ()-[r]->() "
            "RETURN type(r) AS type, count(r) AS count "
            "ORDER BY count DESC"
        )

        return {
            "total_nodes": node_count[0]["count"] if node_count else 0,
            "total_relationships": rel_count[0]["count"] if rel_count else 0,
            "label_counts": {r["label"]: r["count"] for r in label_counts},
            "relationship_type_counts": {
                r["type"]: r["count"] for r in rel_type_counts
            },
        }

    def clear_graph(self):
        self.run_query("MATCH (n) DETACH DELETE n")

    def get_full_graph(self, limit: int = 500) -> dict:
        records = self.run_query(
            "MATCH (n) "
            "OPTIONAL MATCH (n)-[r]->(m) "
            "RETURN n, r, m "
            "LIMIT $limit",
            {"limit": limit},
        )

        nodes = {}
        links = []
        for rec in records:
            n = rec["n"]
            if n and n.get("id") not in nodes:
                nodes[n["id"]] = {
                    "id": n["id"],
                    "name": n.get("name", ""),
                    "label": n.get("_label", ""),
                    **{k: v for k, v in n.items() if k not in ("id",)},
                }

            m = rec.get("m")
            if m and m.get("id") not in nodes:
                nodes[m["id"]] = {
                    "id": m["id"],
                    "name": m.get("name", ""),
                    "label": m.get("_label", ""),
                    **{k: v for k, v in m.items() if k not in ("id",)},
                }

            r = rec.get("r")
            if r and n and m:
                links.append(
                    {
                        "source": n["id"],
                        "target": m["id"],
                        "type": r.get("_type", ""),
                    }
                )

        return {"nodes": list(nodes.values()), "links": links}


neo4j_client = Neo4jClient()
