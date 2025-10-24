from fastapi import APIRouter, HTTPException
from bson import ObjectId
from datetime import datetime
from ..services.mongo import get_db
from app.conex_neo import get_driver

router = APIRouter(prefix="/turnos", tags=["Turnos"])

def serialize_doc(doc: dict) -> dict:
    out = {}
    for k, v in doc.items():
        out[k] = str(v) if isinstance(v, ObjectId) else v
    return out

@router.get("/")
def list_turnos():
    db = get_db()
    docs = [serialize_doc(t) for t in db["turnos"].find()]
    return {"count": len(docs), "turnos": docs}

@router.get("/{id}")
def get_turno_by_id(id: str):
    db = get_db()
    try:
        oid = ObjectId(id)
    except Exception:
        raise HTTPException(status_code=400, detail="ID inválido")
    turno = db["turnos"].find_one({"_id": oid})
    if not turno:
        raise HTTPException(status_code=404, detail="Turno no encontrado")
    return serialize_doc(turno)

@router.get("/medico/{matricula}")
def get_turnos_por_medico(matricula: str):
    db = get_db()
    medico = db["medicos"].find_one({"matricula": matricula})
    if not medico:
        raise HTTPException(status_code=404, detail=f"Médico con matrícula {matricula} no encontrado")
    medico_id = str(medico["_id"])
    turnos = [serialize_doc(t) for t in db["turnos"].find({"id_medico": medico_id})]
    return {"count": len(turnos), "medico": {"matricula": matricula, "nombre": medico.get("username")}, "turnos": turnos}

@router.get("/paciente/{dni}")
def get_turnos_por_paciente(dni: str):
    db = get_db()
    paciente = db["pacientes"].find_one({"dni": dni})
    if not paciente:
        raise HTTPException(status_code=404, detail=f"Paciente con DNI {dni} no encontrado")
    paciente_id = str(paciente["_id"])
    turnos = [serialize_doc(t) for t in db["turnos"].find({"id_paciente": paciente_id})]
    return {"count": len(turnos), "paciente": {"dni": dni, "nombre": paciente.get("nombre")}, "turnos": turnos}

@router.post("/")
def crear_turno(turno: dict):
    """
    Crea un turno usando matricula del médico y DNI del paciente.
    Requiere: matricula, dni, fecha_hora.
    """
    db = get_db()
    
    # Validar campos requeridos
    required_fields = ["matricula", "dni", "fecha_hora"]
    if not all(field in turno for field in required_fields):
        raise HTTPException(status_code=400, detail="Faltan campos obligatorios: matricula, dni, fecha_hora")
    
    # Buscar paciente por DNI
    paciente = db["pacientes"].find_one({"dni": turno.get("dni")})
    if not paciente:
        raise HTTPException(status_code=404, detail=f"Paciente con DNI {turno.get('dni')} no encontrado")
    
    # Buscar médico por matrícula
    medico = db["medicos"].find_one({"matricula": turno.get("matricula")})
    if not medico:
        raise HTTPException(status_code=404, detail=f"Médico con matrícula {turno.get('matricula')} no encontrado")
    
    # Parsear fecha_hora de string a datetime
    try:
        fecha_hora_dt = datetime.fromisoformat(turno.get("fecha_hora").replace("Z", "+00:00"))
    except (ValueError, AttributeError):
        raise HTTPException(status_code=400, detail="Formato de fecha_hora inválido. Use ISO 8601 (ej: 2025-10-23T20:21:06)")
    
    # Crear turno con los ObjectIds internos
    nuevo_turno = {
        "id_paciente": str(paciente["_id"]),
        "id_medico": str(medico["_id"]),
        "fecha_hora": fecha_hora_dt,
        "estado": "pendiente"
    }
    result = db["turnos"].insert_one(nuevo_turno)
    turno_id = str(result.inserted_id)
    nuevo_turno["_id"] = turno_id

    # Agregar el ID del turno al array de turnos del paciente
    db["pacientes"].update_one(
        {"_id": paciente["_id"]},
        {"$push": {"turnos": turno_id}}
    )

    # Crear relación (Medico)-[:ATIENDE]->(Paciente) en Neo4j
    neo_status = "ok"
    try:
        driver = get_driver()
        driver.execute_query(
            (
                "MERGE (m:Medico {matricula: $matricula})\n"
                "MERGE (p:Paciente {dni: $dni})\n"
                "MERGE (m)-[r:ATIENDE]->(p)\n"
                "SET r.fecha_hora = $fecha_hora"
            ),
            matricula=medico.get("matricula"),
            dni=paciente.get("dni"),
            fecha_hora=nuevo_turno.get("fecha_hora"),
            database_="neo4j",
        )
    except Exception as e:
        neo_status = f"error: {e}"

    return {"status": "ok", "mensaje": "Turno creado", "turno": nuevo_turno, "neo4j": neo_status}

@router.delete("/{id}")
def eliminar_turno(id: str):
    db = get_db()
    try:
        oid = ObjectId(id)
    except Exception:
        raise HTTPException(status_code=400, detail="ID inválido")
    
    # Buscar el turno antes de eliminarlo para obtener los IDs
    turno = db["turnos"].find_one({"_id": oid})
    if not turno:
        raise HTTPException(status_code=404, detail="Turno no encontrado")
    
    # Eliminar el turno
    result = db["turnos"].delete_one({"_id": oid})
    
    # Eliminar el ID del turno del array de turnos del paciente
    db["pacientes"].update_one(
        {"_id": ObjectId(turno["id_paciente"])},
        {"$pull": {"turnos": id}}
    )
    
    return {"status": "ok", "mensaje": "Turno eliminado"}
