from fastapi import APIRouter, HTTPException
from bson import ObjectId
from ..services.mongo import get_db
from app.conex_neo import get_driver

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

@router.post("/")
def create_medico(medico: dict):
    db = get_db()
    required_fields = ["nombre", "apellido", "matricula", "especialidad"]

    if not all(field in medico for field in required_fields):
        raise HTTPException(status_code=400, detail="Faltan campos obligatorios")

    if db["medicos"].find_one({"matricula": medico["matricula"]}):
        raise HTTPException(status_code=400, detail="La matrícula ya existe")

    result = db["medicos"].insert_one(medico)

    # Crear/MERGE del nodo del médico en Neo4j
    neo_status = "ok"
    try:
        driver = get_driver()
        driver.execute_query(
            (
                "MERGE (m:Medico {matricula: $matricula})\n"
                "SET m.nombre = $nombre,\n"
                "    m.apellido = $apellido,\n"
                "    m.especialidad = $especialidad,\n"
                "    m.email = $email"
            ),
            matricula=medico.get("matricula"),
            nombre=medico.get("nombre"),
            apellido=medico.get("apellido"),
            especialidad=medico.get("especialidad"),
            email=medico.get("email"),
            database_="neo4j",
        )
    except Exception as e:
        neo_status = f"error: {e}"

    return {
        "_id": str(result.inserted_id),
        "mensaje": "Médico creado correctamente",
        "neo4j": neo_status,
    }

@router.delete("/{matricula}")
def delete_medico(matricula: str):
    db = get_db()
    result = db["medicos"].delete_one({"matricula": matricula})

    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Médico no encontrado")

    return {"mensaje": f"Médico con matrícula {matricula} eliminado correctamente"}