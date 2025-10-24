from distutils import errors
import os
from pymongo import MongoClient, errors
from dotenv import load_dotenv

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI", "mongodb://mongodb:27017/")  # valor por defecto si no está en .env
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