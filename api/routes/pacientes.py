import datetime
import random
from fastapi import APIRouter, HTTPException, Query
from bson import ObjectId
from datetime import datetime
from pydantic import BaseModel
from ..services.mongo import get_db
from ..services.redis import get_redis

router = APIRouter(prefix="/pacientes", tags=["Pacientes"])

class SintomaIn(BaseModel):
    sintoma: str

def serialize_doc(doc: dict) -> dict:
    if not doc:
        return doc
    out = {}
    for k, v in doc.items():
        out[k] = str(v) if isinstance(v, ObjectId) else v
    return out

@router.get("/")
def list_pacientes():
    db = get_db()
    docs = [serialize_doc(p) for p in db["pacientes"].find()]
    return {"count": len(docs), "pacientes": docs}

@router.get("/{dni}")
def get_paciente(dni: str):
    db = get_db()
    p = db["pacientes"].find_one({"dni": dni})
    if not p:
        raise HTTPException(status_code=404, detail="Paciente no encontrado")
    return serialize_doc(p)

@router.get("/id/{id}")
def get_paciente_by_id(id: str):
    db = get_db()
    try:
        oid = ObjectId(id)
    except Exception:
        raise HTTPException(status_code=400, detail="ID inválido")
    p = db["pacientes"].find_one({"_id": oid})
    if not p:
        raise HTTPException(status_code=404, detail="Paciente no encontrado")
    return serialize_doc(p)

@router.get("/frecuencias_por_fecha")
def frecuencias_por_fecha(fecha: str = Query(..., description="Fecha en formato YYYY-MM-DD")):
    """
    Devuelve todas las frecuencias cardíacas registradas en MongoDB
    para todos los pacientes en la fecha indicada.
    """
    db = get_db()
    pacientes = db["pacientes"].find()
    resultado = []

    for paciente in pacientes:
        registros = paciente.get("mayor_frecuencia_cardiaca_dia", [])
        frecuencias_fecha = [
            r["ritmo_cardiaco"] for r in registros if r.get("fecha") == fecha
        ]

        if frecuencias_fecha:
            resultado.append({
                "nombre": paciente.get("nombre"),
                "dni": paciente.get("dni"),
                "frecuencias": frecuencias_fecha
            })

    if not resultado:
        raise HTTPException(status_code=404, detail="No hay registros de frecuencia para esa fecha")

    return {
        "fecha": fecha,
        "pacientes": resultado
    }

@router.post("/{dni}/sintomas")
def generar_sintomas(dni: str, request: SintomaIn):
    """
    Agrega un síntoma en Redis para el paciente con el DNI indicado.
    """
    db = get_db()
    paciente = db["pacientes"].find_one({"dni": dni})
    if not paciente:
        raise HTTPException(status_code=404, detail=f"Paciente con DNI {dni} no encontrado en MongoDB.")

    try:
        r = get_redis()  # usamos tu helper que ya lee host y puerto del .env
        key = f"sintomas:paciente:{dni}"
        r.rpush(key, request.sintoma)

        return {
            "status": "ok",
            "dni": dni,
            "sintoma": request.sintoma,
            "mensaje": f"Síntoma '{request.sintoma}' agregado en Redis para paciente {dni}.",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al guardar síntoma en Redis: {str(e)}")

@router.post("/{dni}/guardar_sintomas")
def guardar_sintomas_diarios(dni: str):
    """
    Guarda los síntomas del día desde Redis en MongoDB para el paciente indicado,
    evitando duplicados por fecha y limpiando Redis después.
    """
    db = get_db()
    r = get_redis()

    paciente = db["pacientes"].find_one({"dni": dni})
    if not paciente:
        raise HTTPException(status_code=404, detail=f"Paciente con DNI {dni} no encontrado en MongoDB.")

    key = f"sintomas:paciente:{dni}"
    sintomas_redis = [s.decode() if isinstance(s, bytes) else s for s in r.lrange(key, 0, -1)]
    if not sintomas_redis:
        raise HTTPException(status_code=400, detail=f"No hay síntomas cargados en Redis para el paciente {dni}.")

    fecha_hoy = datetime.now().strftime("%Y-%m-%d")
    sintomas_diarios = paciente.get("sintomas_diarios", [])

    entrada_hoy = next((item for item in sintomas_diarios if item["fecha"] == fecha_hoy), None)

    if entrada_hoy:
        # Solo agregamos síntomas nuevos
        sintomas_existentes = set(entrada_hoy["sintomas"])
        nuevos_sintomas = [s for s in sintomas_redis if s not in sintomas_existentes]

        if nuevos_sintomas:
            db["pacientes"].update_one(
                {"dni": dni, "sintomas_diarios.fecha": fecha_hoy},
                {"$addToSet": {"sintomas_diarios.$.sintomas": {"$each": nuevos_sintomas}}}
            )
            mensaje = f"🔄 Actualizados síntomas del día {fecha_hoy} en MongoDB para paciente {dni}."
        else:
            mensaje = f"⏸️ No hay nuevos síntomas para agregar hoy en MongoDB."
    else:
        # Creamos una nueva entrada
        nuevo_registro = {
            "fecha": fecha_hoy,
            "sintomas": list(set(sintomas_redis))  # <-- eliminamos duplicados antes de guardar
        }
        db["pacientes"].update_one(
            {"dni": dni},
            {"$push": {"sintomas_diarios": nuevo_registro}}
        )
        mensaje = f"✅ Se creó el registro de síntomas del día {fecha_hoy} en MongoDB para paciente {dni}."

    # Limpiamos Redis
    r.delete(key)

    return {
        "status": "ok",
        "dni": dni,
        "fecha": fecha_hoy,
        "sintomas_guardados": sintomas_redis,
        "mensaje": mensaje
    }

@router.post("/{dni}/generar_frecuencia")
def generar_frecuencia_cardiaca(dni: str):
    db = get_db()
    r = get_redis()
    paciente = db["pacientes"].find_one({"dni": dni})
    if not paciente:
        raise HTTPException(status_code=404, detail=f"Paciente con DNI {dni} no encontrado")

    key = f"frecuencia:paciente:{dni}"
    frecuencia = random.randint(60, 120)
    fecha = datetime.now().isoformat()
    r.zadd(key, {fecha: frecuencia})
    r.expire(key, 86400)
    return {"status": "ok", "dni": dni, "frecuencia": frecuencia, "fecha": fecha}

@router.post("/{dni}/actualizar_frecuencia")
def actualizar_mayor_frecuencia(dni: str):
    db = get_db()
    r = get_redis()
    key = f"frecuencia:paciente:{dni}"

    resultado = r.zrevrange(key, 0, 0, withscores=True)
    if not resultado:
        raise HTTPException(status_code=404, detail=f"No hay datos de frecuencia cardíaca en Redis para {dni}")

    fecha_completa, frecuencia = resultado[0]
    fecha_completa = fecha_completa.decode("utf-8") if isinstance(fecha_completa, bytes) else fecha_completa
    fecha_dia = datetime.fromisoformat(fecha_completa).strftime("%Y-%m-%d")

    paciente = db["pacientes"].find_one({"dni": dni, "mayor_frecuencia_cardiaca_dia.fecha": fecha_dia})
    if paciente:
        raise HTTPException(status_code=400, detail=f"Ya existe un registro para la fecha {fecha_dia} del paciente {dni}")

    nuevo_registro = {"fecha": fecha_dia, "ritmo_cardiaco": frecuencia}
    db["pacientes"].update_one({"dni": dni}, {"$push": {"mayor_frecuencia_cardiaca_dia": nuevo_registro}})

    return {"status": "ok", "dni": dni, "registro": nuevo_registro}