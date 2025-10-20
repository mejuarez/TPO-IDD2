# paciente.py
from conex_mongo import get_mongo_connection
from bson import ObjectId
import datetime
from medico import existe_medico

db = get_mongo_connection()
pacientes = db["pacientes"]

def crear_paciente(nombre, dni, fecha_nacimiento, email, telefono, tipo_de_sangre, medico_id=None):
    """Crea un paciente nuevo con historial clínico vacío y valida médico"""
    if pacientes.find_one({"dni": dni}):
        return {"status": "error", "message": "El paciente ya existe"}

    if medico_id and not existe_medico(medico_id):
        return {"status": "error", "message": "Médico no existe"}

    paciente_doc = {
        "nombre": nombre,
        "dni": dni,
        "fecha_nacimiento": fecha_nacimiento,
        "email": email,
        "telefono": telefono,
        "tipo_de_sangre": tipo_de_sangre,
        "medico_id": ObjectId(medico_id) if medico_id else None,
        "historia_clinica": [],
        "created_at": datetime.datetime.utcnow()
    }
    paciente_id = pacientes.insert_one(paciente_doc).inserted_id
    return {"status": "ok", "message": "Paciente creado exitosamente", "id": paciente_id}

def existe_paciente(dni):
    return pacientes.find_one({"dni": dni}) is not None

def editar_paciente(dni, nuevos_datos):
    """Actualiza los datos de un paciente existente por DNI y valida médico si se cambia"""
    if "medico_id" in nuevos_datos and nuevos_datos["medico_id"] is not None:
        if not existe_medico(nuevos_datos["medico_id"]):
            return {"status": "error", "message": "Médico no existe"}
        nuevos_datos["medico_id"] = ObjectId(nuevos_datos["medico_id"])
    
    result = pacientes.update_one({"dni": dni}, {"$set": nuevos_datos})
    if result.matched_count == 0:
        return {"status": "error", "message": "Paciente no encontrado"}
    return {"status": "ok", "message": "Datos del paciente actualizados"}

def eliminar_paciente(dni):
    result = pacientes.delete_one({"dni": dni})
    if result.deleted_count == 0:
        return {"status": "error", "message": "Paciente no encontrado"}
    return {"status": "ok", "message": "Paciente eliminado correctamente"}

def agregar_visita(dni, fecha, diagnostico, tratamiento, observaciones, examenes=None, notas_medico=""):
    """Agrega una visita al historial clínico de un paciente con timestamp automático"""
    visita = {
        "fecha": fecha if isinstance(fecha, datetime.datetime) else datetime.datetime.strptime(fecha, "%Y-%m-%d"),
        "diagnostico": diagnostico,
        "tratamiento": tratamiento,
        "observaciones": observaciones,
        "examenes": examenes if examenes else [],
        "notas_medico": notas_medico,
        "created_at": datetime.datetime.utcnow()
    }
    resultado = pacientes.update_one(
        {"dni": dni},
        {"$push": {"historia_clinica": visita}}
    )
    if resultado.modified_count > 0:
        return {"status": "ok", "message": "Visita agregada"}
    return {"status": "error", "message": "Paciente no encontrado"}

def obtener_paciente(dni, filtrar_sensible=True):
    """Devuelve datos del paciente, filtra info sensible si se indica"""
    projection = None
    if filtrar_sensible:
        projection = {
            "email": 0,
            "telefono": 0,
            "historia_clinica.notas_medico": 0
        }
    paciente = pacientes.find_one({"dni": dni}, projection)
    return paciente

def mostrar_historial(dni, ver_notas=False):
    paciente = pacientes.find_one({"dni": dni}, {"historia_clinica": 1, "_id": 0})
    if not paciente:
        return None
    historia = paciente.get("historia_clinica", [])
    if not ver_notas:
        for v in historia:
            v.pop("notas_medico", None)
    return historia
