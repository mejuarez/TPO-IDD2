# medico.py
import bcrypt
from conex_mongo import get_mongo_connection
from datetime import datetime

db = get_mongo_connection()
medicos = db["medicos"]

def crear_medico(matricula, username, password, especialidad, email):
    """Crea un médico nuevo si no existe"""
    if medicos.find_one({"matricula": matricula}):
        return {"status": "error", "message": "El médico ya existe"}

    hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    medico_doc = {
        "matricula": matricula,
        "username": username,
        "password": hashed,
        "especialidad": especialidad,
        "email": email,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }
    medico_id = medicos.insert_one(medico_doc).inserted_id
    return {"status": "ok", "message": "Médico creado exitosamente", "id": medico_id}

def existe_medico(matricula):
    return medicos.find_one({"matricula": matricula}) is not None

def editar_medico(matricula, nuevos_datos):
    """Actualiza los datos de un médico y timestamp"""
    nuevos_datos["updated_at"] = datetime.utcnow()
    result = medicos.update_one({"matricula": matricula}, {"$set": nuevos_datos})
    if result.matched_count == 0:
        return {"status": "error", "message": "Médico no encontrado"}
    return {"status": "ok", "message": "Datos actualizados correctamente"}

def eliminar_medico(matricula):
    result = medicos.delete_one({"matricula": matricula})
    if result.deleted_count == 0:
        return {"status": "error", "message": "Médico no encontrado"}
    return {"status": "ok", "message": "Médico eliminado correctamente"}

def obtener_medico_por_matricula(matricula, ocultar_sensible=True):
    """Devuelve los datos de un médico, filtrando datos sensibles si se indica"""
    medico = medicos.find_one({"matricula": matricula})
    if not medico:
        return None
    if ocultar_sensible:
        medico.pop("password", None)
    return medico
