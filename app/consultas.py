# consultas.py
from paciente import pacientes
from medico import medicos
from bson import ObjectId

# -----------------------
# Funciones de pacientes
# -----------------------
def obtener_paciente_por_dni(dni):
    return pacientes.find_one({"dni": dni})

def obtener_pacientes_por_tipo_sangre(tipo):
    return list(pacientes.find({"tipo_de_sangre": tipo}))

def obtener_pacientes_por_medico(medico_id):
    return list(pacientes.find({"medico_id": ObjectId(medico_id)}))

# -----------------------
# Funciones de médicos
# -----------------------
def obtener_medico_por_matricula(matricula):
    return medicos.find_one({"matricula": matricula})

def obtener_medicos_por_especialidad(especialidad):
    return list(medicos.find({"especialidad": especialidad}))
