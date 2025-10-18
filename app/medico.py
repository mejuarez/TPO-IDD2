# vidasana/app/prueba/medico.py
import bcrypt
from conex_mongo import get_mongo_connection

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
        "email": email
    }
    medico_id = medicos.insert_one(medico_doc).inserted_id  # Guardamos el ObjectId
    return {"status": "ok", "message": "Médico creado exitosamente", "id": medico_id}  # <-- devuelve ObjectId


def existe_medico(matricula):
    """Verifica si existe un médico"""
    return medicos.find_one({"matricula": matricula}) is not None

def editar_medico(matricula, nuevos_datos):
    """Actualiza los datos de un médico existente"""
    result = medicos.update_one({"matricula": matricula}, {"$set": nuevos_datos})
    if result.matched_count == 0:
        return {"status": "error", "message": "Médico no encontrado"}
    return {"status": "ok", "message": "Datos actualizados correctamente"}

def eliminar_medico(matricula):
    """Elimina un médico por su matrícula"""
    result = medicos.delete_one({"matricula": matricula})
    if result.deleted_count == 0:
        return {"status": "error", "message": "Médico no encontrado"}
    return {"status": "ok", "message": "Médico eliminado correctamente"}

def obtener_medico_por_matricula(matricula):
    """Devuelve el documento del médico por matricula"""
    return medicos.find_one({"matricula": matricula})
