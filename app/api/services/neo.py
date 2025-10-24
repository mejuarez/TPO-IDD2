import os
from pathlib import Path
from neo4j import GraphDatabase
from dotenv import load_dotenv

# Cargar .env desde la raíz del proyecto
project_root = Path(__file__).resolve().parent.parent.parent.parent
dotenv_path = project_root / ".env"
load_dotenv(dotenv_path=dotenv_path)

# Configuración de conexión a Neo4j
NEO4J_URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "neo4jpassword")

_driver = None

def get_driver():
    """Devuelve el driver activo de Neo4j para usar en otros módulos"""
    global _driver
    if _driver is None:
        _driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))
    return _driver

def close_driver():
    """Cierra la conexión con Neo4j"""
    global _driver
    if _driver is not None:
        _driver.close()
        _driver = None
