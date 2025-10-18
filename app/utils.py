# utils.py
from bson import ObjectId

def limpiar_paciente(paciente_doc):
    """Devuelve un paciente con solo la info necesaria"""
    if not paciente_doc:
        return None
    return {
        "id": str(paciente_doc["_id"]),
        "nombre": paciente_doc.get("nombre"),
        "dni": paciente_doc.get("dni"),
        "fecha_nacimiento": paciente_doc.get("fecha_nacimiento"),
        "email": paciente_doc.get("email"),
        "telefono": paciente_doc.get("telefono"),
        "tipo_de_sangre": paciente_doc.get("tipo_de_sangre"),
        "medico_id": str(paciente_doc.get("medico_id")) if paciente_doc.get("medico_id") else None,
        "historia_clinica": paciente_doc.get("historia_clinica", [])
    }

def limpiar_medico(medico_doc):
    """Devuelve un médico con solo la info necesaria"""
    if not medico_doc:
        return None
    return {
        "id": str(medico_doc["_id"]),
        "matricula": medico_doc.get("matricula"),
        "username": medico_doc.get("username"),
        "especialidad": medico_doc.get("especialidad"),
        "email": medico_doc.get("email")
    }

def limpiar_lista(documentos, tipo="paciente"):
    """Limpia una lista de documentos"""
    if tipo == "paciente":
        return [limpiar_paciente(d) for d in documentos]
    else:
        return [limpiar_medico(d) for d in documentos]
