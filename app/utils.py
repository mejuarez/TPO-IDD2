# utils.py
def limpiar_paciente(paciente_doc):
    if not paciente_doc:
        return None
    return {
        "nombre": paciente_doc.get("nombre"),
        "dni": paciente_doc.get("dni"),
        "fecha_nacimiento": paciente_doc.get("fecha_nacimiento"),
        "tipo_de_sangre": paciente_doc.get("tipo_de_sangre"),
        "medico_id": paciente_doc.get("medico_id"),
        "historia_clinica": paciente_doc.get("historia_clinica", [])
    }

def limpiar_medico(medico_doc):
    if not medico_doc:
        return None
    return {
        "matricula": medico_doc.get("matricula"),
        "username": medico_doc.get("username"),
        "especialidad": medico_doc.get("especialidad"),
        "email": medico_doc.get("email")
    }

def limpiar_lista(documentos, tipo="paciente"):
    if tipo == "paciente":
        return [limpiar_paciente(d) for d in documentos]
    else:
        return [limpiar_medico(d) for d in documentos]
