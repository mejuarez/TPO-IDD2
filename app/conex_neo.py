# app/conex_neo.py
from neo4j import GraphDatabase

# ⚙️ Configuración de conexión a Neo4j
URI = "bolt://localhost:7687"
USER = "neo4j"
PASSWORD = "neo4jpassword"  

driver = GraphDatabase.driver(URI, auth=(USER, PASSWORD))

def get_driver():
    """Devuelve el driver activo para usar en otros módulos"""
    return driver
