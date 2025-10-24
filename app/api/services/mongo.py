from distutils import errors
import os
from pathlib import Path
from pymongo import MongoClient, errors
from dotenv import load_dotenv

# Cargar .env desde la raíz del proyecto (4 niveles arriba desde este archivo)
project_root = Path(__file__).resolve().parent.parent.parent.parent
dotenv_path = project_root / ".env"
load_dotenv(dotenv_path=dotenv_path)

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/")  # valor por defecto localhost para dev local
DB_NAME = os.getenv("MONGO_DB", "vidasana")

_client = None

def get_client():
    global _client
    if _client is None:
        try:
            _client = MongoClient(
                MONGO_URI,
                serverSelectionTimeoutMS=20000,
                connectTimeoutMS=20000
            )
            _client.admin.command("ping")  # verifica conexión
        except errors.ServerSelectionTimeoutError as e:
            raise RuntimeError(f"No se puede conectar a MongoDB en {MONGO_URI}: {e}")
    return _client

def get_db():
    client = get_client()
    return client[DB_NAME]