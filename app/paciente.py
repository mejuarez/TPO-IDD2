# paciente.py
from conex_mongo import get_mongo_connection
from bson import ObjectId
import datetime

db = get_mongo_connection()
pacientes = db["pacientes"]

def crear_paciente(nombre, dni, fecha_nacimiento, email, telefono, tipo_de_sangre, medico_id=None):
    """Crea un paciente nuevo con historial clínico vacío"""
    if pacientes.find_one({"dni": dni}):
        return {"status": "error", "message": "El paciente ya existe"}

    paciente_doc = {
        "nombre": nombre,
        "dni": dni,
        "fecha_nacimiento": fecha_nacimiento,
        "email": email,
        "telefono": telefono,
        "tipo_de_sangre": tipo_de_sangre,
        "medico_id": ObjectId(medico_id) if medico_id else None,
        "historia_clinica": []
    }
    paciente_id = pacientes.insert_one(paciente_doc).inserted_id
    return {"status": "ok", "message": "Paciente creado exitosamente", "id": paciente_id}


def existe_paciente(dni):
    """Verifica si existe un paciente por DNI"""
    return pacientes.find_one({"dni": dni}) is not None


def editar_paciente(dni, nuevos_datos):
    """Actualiza los datos de un paciente existente por DNI"""
    if "medico_id" in nuevos_datos and nuevos_datos["medico_id"] is not None:
        nuevos_datos["medico_id"] = ObjectId(nuevos_datos["medico_id"])
    
    result = pacientes.update_one({"dni": dni}, {"$set": nuevos_datos})
    if result.matched_count == 0:
        return {"status": "error", "message": "Paciente no encontrado"}
    return {"status": "ok", "message": "Datos del paciente actualizados"}


def eliminar_paciente(dni):
    """Elimina un paciente por DNI"""
    result = pacientes.delete_one({"dni": dni})
    if result.deleted_count == 0:
        return {"status": "error", "message": "Paciente no encontrado"}
    return {"status": "ok", "message": "Paciente eliminado correctamente"}

def agregar_visita(dni, fecha, diagnostico, tratamiento, observaciones, examenes=None, notas_medico=""):
    """Agrega una visita al historial clínico de un paciente"""
    visita = {
        "fecha": fecha if isinstance(fecha, datetime.datetime) else datetime.datetime.strptime(fecha, "%Y-%m-%d"),
        "diagnostico": diagnostico,
        "tratamiento": tratamiento,
        "observaciones": observaciones,
        "examenes": examenes if examenes else [],
        "notas_medico": notas_medico
    }

    resultado = pacientes.update_one(
        {"dni": dni},
        {"$push": {"historia_clinica": visita}}
    )
    if resultado.modified_count > 0:
        return {"status": "ok", "message": "Visita agregada"}
    return {"status": "error", "message": "Paciente no encontrado"}


def mostrar_historial(dni):
    """Devuelve el historial clínico completo de un paciente"""
    paciente = pacientes.find_one({"dni": dni}, {"historia_clinica": 1, "_id": 0})
    if paciente:
        return paciente.get("historia_clinica", [])
    return None

