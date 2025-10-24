from fastapi import APIRouter, Body, Depends, HTTPException
from pydantic import BaseModel

from app.api.services.auth import crear_sesion, verificar_sesion

router = APIRouter(prefix="/auth", tags=["Auth"])

class LoginIn(BaseModel):
    dni: str
    password: str  # si tenés password, sino solo dni para demo

@router.post("/login/paciente")

def login_paciente(login: LoginIn):
    from app.api.services.mongo import get_db
    db = get_db()
    paciente = db["pacientes"].find_one({"dni": login.dni})
    if not paciente:
        raise HTTPException(status_code=404, detail="Paciente no encontrado")

    # Aquí podrías validar password si lo tenés
    token = crear_sesion("paciente", login.dni)
    return {"token": token, "mensaje": "Login exitoso"}

@router.get("/mis_datos")
def mis_datos(usuario_info: dict = Depends(verificar_sesion)):
    # usuario_info viene de Redis
    return {
        "mensaje": f"Hola {usuario_info['usuario_tipo']} con ID {usuario_info['usuario_id']}"
    }