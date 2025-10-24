from fastapi import FastAPI
from api.routes import pacientes, medicos,auth

app = FastAPI(title="VidaSana API - minimal")

app.include_router(pacientes.router)
app.include_router(medicos.router)
app.include_router(auth.router)

""""
# ...existing code...
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from datetime import date, datetime
# Cambiado a import relativo (services está en app/api/services)
from .services.mongo import get_db
from .services.redis import get_redis
from bson import ObjectId
# ...existing code...


app = FastAPI(title="VidaSana API - minimal")

class SintomaIn(BaseModel):
    sintoma: str

# helper para serializar ObjectId
def serialize_doc(doc: dict) -> dict:
    if not doc:
        return doc
    out = {}
    for k, v in doc.items():
        if isinstance(v, ObjectId):
            out[k] = str(v)
        else:
            out[k] = v
    return out

@app.get("/medicos")
def list_medicos():
    db = get_db()
    docs = []
    for m in db["medicos"].find({}, {"password": 0}):
        docs.append(serialize_doc(m))
    return {"count": len(docs), "medicos": docs}

# obtener médico por matrícula
@app.get("/medicos/{matricula}")
def get_medico(matricula: str):
    db = get_db()
    m = db["medicos"].find_one({"matricula": matricula}, {"password": 0})
    if not m:
        raise HTTPException(status_code=404, detail="Médico no encontrado")

@app.post("/pacientes/{dni}/sintomas")
def agregar_sintoma(dni: str, body: SintomaIn):
    r = get_redis()
    today = date.today().isoformat()
    key = f"sintomas:{dni}:{today}"
    try:
        r.rpush(key, body.sintoma)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    return {"status":"ok", "key": key, "sintoma": body.sintoma, "ts": datetime.utcnow().isoformat()}

@app.get("/pacientes/{dni}/sintomas")
def listar_sintomas_dia(dni: str, fecha: str = None):
    r = get_redis()
    fecha = fecha or date.today().isoformat()
    key = f"sintomas:{dni}:{fecha}"
    try:
        items = r.lrange(key, 0, -1)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    return {"dni": dni, "fecha": fecha, "sintomas": items}

# listar todos los pacientes
@app.get("/pacientes")
def list_pacientes():
    db = get_db()
    docs = []
    for p in db["pacientes"].find():
        docs.append(serialize_doc(p))
    return {"count": len(docs), "pacientes": docs}

# obtener paciente por DNI
@app.get("/pacientes/{dni}")
def get_paciente(dni: str):
    db = get_db()
    p = db["pacientes"].find_one({"dni": dni})
    if not p:
        raise HTTPException(status_code=404, detail="Paciente no encontrado")
    return serialize_doc(p)

# obtener paciente por ObjectId
@app.get("/pacientes/id/{id}")
def get_paciente_by_id(id: str):
    db = get_db()
    try:
        oid = ObjectId(id)
    except Exception:
        raise HTTPException(status_code=400, detail="ID inválido")
    p = db["pacientes"].find_one({"_id": oid})
    if not p:
        raise HTTPException(status_code=404, detail="Paciente no encontrado")
"""