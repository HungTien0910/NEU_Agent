DISALLOWED = {
    "CREATE",
    "MERGE",
    "SET",
    "DELETE",
    "DETACH",
    "REMOVE",
    "DROP",
    "CALL",
    "LOAD",
    "CSV",
    "APOC",
    "PERIODIC",
}


def validate_cypher(cypher: str) -> None:
    tokens = {t.upper() for t in cypher.replace("\n", " ").split()}
    illegal = tokens & DISALLOWED
    if illegal:
        raise ValueError(f"Cypher contains illegal tokens: {sorted(illegal)}")
