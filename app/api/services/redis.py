import os
from pathlib import Path
import redis
from dotenv import load_dotenv

# Cargar .env desde la raíz del proyecto
project_root = Path(__file__).resolve().parent.parent.parent.parent
dotenv_path = project_root / ".env"
load_dotenv(dotenv_path=dotenv_path)

REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))

def get_redis():
    return redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)