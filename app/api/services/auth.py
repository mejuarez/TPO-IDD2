import secrets
from .redis import get_redis
from datetime import timedelta
from fastapi import Header, HTTPException

def generar_token():
    """Genera un token seguro aleatorio"""
    return secrets.token_hex(16)

def crear_sesion(usuario_tipo: str, usuario_id: str):
    """
    Crea una sesión en Redis para el usuario con TTL de 1 hora.
    usuario_tipo: "paciente" o "medico"
    usuario_id: dni para paciente o _id para medico
    """
    r = get_redis()
    token = generar_token()
    key = f"sesion:{token}"
    # Guardamos info mínima en Redis
    valor = {
        "usuario_tipo": usuario_tipo,
        "usuario_id": usuario_id
    }
    r.hset(key, mapping=valor)
    r.expire(key, timedelta(hours=1))
    
    return token

def verificar_sesion(token: str = Header(..., description="Token de sesión")):
    r = get_redis()
    key = f"sesion:{token}"
    if not r.exists(key):
        raise HTTPException(status_code=401, detail="Sesión inválida o expirada")
    # Traemos info del usuario si queremos
    usuario_info = r.hgetall(key)
    return usuario_info