from fastapi import APIRouter, HTTPException
from bson import ObjectId
from ..services.mongo import get_db

router = APIRouter(prefix="/medicos", tags=["Médicos"])

def serialize_doc(doc: dict) -> dict:
    out = {}
    for k, v in doc.items():
        out[k] = str(v) if isinstance(v, ObjectId) else v
    return out

@router.get("/")
def list_medicos():
    db = get_db()
    docs = [serialize_doc(m) for m in db["medicos"].find({}, {"password": 0})]
    return {"count": len(docs), "medicos": docs}

@router.get("/{matricula}")
def get_medico(matricula: str):
    db = get_db()
    m = db["medicos"].find_one({"matricula": matricula}, {"password": 0})
    if not m:
        raise HTTPException(status_code=404, detail="Médico no encontrado")
    return serialize_doc(m)