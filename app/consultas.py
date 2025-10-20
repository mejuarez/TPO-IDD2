# consultas.py
from paciente import pacientes
from medico import medicos
from bson import ObjectId

# ----------------------- Pacientes -----------------------
def obtener_paciente_por_dni(dni):
    return pacientes.find_one({"dni": dni})

def obtener_pacientes_por_tipo_sangre(tipo):
    return list(pacientes.find({"tipo_de_sangre": tipo}))

def obtener_pacientes_por_medico(medico_id):
    try:
        oid = ObjectId(medico_id) if isinstance(medico_id, str) else medico_id
    except:
        return []  
    return list(pacientes.find({"medico_id": oid}))

# ----------------------- Médicos -----------------------
def obtener_medico_por_matricula(matricula):
    medico_doc = medicos.find_one({"matricula": matricula})
    if medico_doc:
        medico_doc.pop("password", None)
    return medico_doc

def obtener_medicos_por_especialidad(especialidad):
    return list(medicos.find({"especialidad": especialidad}))
