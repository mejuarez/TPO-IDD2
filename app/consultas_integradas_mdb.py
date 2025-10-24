# consultas_integradas_mdb.py
from conex_neo import get_driver
from conex_mongo import get_mongo_connection

# 🔹 1. Obtener pacientes atendidos por un médico
def obtener_pacientes_por_medico(nombre_medico):
    driver = get_driver()
    db = get_mongo_connection()
    query = """
    MATCH (p:Paciente)-[:ATENDIDO_POR]->(m:Medico {nombre: $nombre_medico})
    RETURN p.dni AS dni
    """
    with driver.session() as session:
        dnis = [r["dni"] for r in session.run(query, nombre_medico=nombre_medico)]
    if not dnis:
        return []
    return list(db["pacientes"].find({"dni": {"$in": dnis}}, {"_id": 0}))

# 🔹 2. Obtener médicos que atendieron a un paciente
def obtener_medicos_por_paciente(dni_paciente):
    driver = get_driver()
    db = get_mongo_connection()
    query = """
    MATCH (p:Paciente {dni: $dni_paciente})-[:ATENDIDO_POR]->(m:Medico)
    RETURN m.matricula AS matricula
    """
    with driver.session() as session:
        matriculas = [r["matricula"] for r in session.run(query, dni_paciente=dni_paciente)]
    if not matriculas:
        return []
    return list(db["medicos"].find({"matricula": {"$in": matriculas}}, {"_id": 0}))

# 🔹 3. Obtener toda la red médico–paciente
def obtener_red_medico_paciente():
    driver = get_driver()
    db = get_mongo_connection()
    query = """
    MATCH (p:Paciente)-[:ATENDIDO_POR]->(m:Medico)
    RETURN p.dni AS dni_paciente, m.matricula AS matricula_medico
    """
    relaciones = []
    with driver.session() as session:
        for record in session.run(query):
            paciente = db["pacientes"].find_one({"dni": record["dni_paciente"]}, {"_id": 0})
            medico = db["medicos"].find_one({"matricula": record["matricula_medico"]}, {"_id": 0})
            if paciente and medico:
                relaciones.append({"paciente": paciente, "medico": medico})
    return relaciones

# 🔹 4. Cantidad de pacientes por médico
def cantidad_pacientes_por_medico():
    driver = get_driver()
    db = get_mongo_connection()
    query = """
    MATCH (p:Paciente)-[:ATENDIDO_POR]->(m:Medico)
    RETURN m.matricula AS matricula_medico, count(p) AS total_pacientes
    """
    resultados = []
    with driver.session() as session:
        for record in session.run(query):
            medico = db["medicos"].find_one({"matricula": record["matricula_medico"]}, {"_id":0})
            if medico:
                resultados.append({"medico": medico, "total_pacientes": record["total_pacientes"]})
    return resultados

# 🔹 5. Pacientes sin médico asignado
def pacientes_sin_medico():
    driver = get_driver()
    db = get_mongo_connection()
    query = """
    MATCH (p:Paciente)
    WHERE NOT (p)-[:ATENDIDO_POR]->(:Medico)
    RETURN p.dni AS dni_paciente
    """
    pacientes = []
    with driver.session() as session:
        for record in session.run(query):
            paciente = db["pacientes"].find_one({"dni": record["dni_paciente"]}, {"_id":0})
            if paciente:
                pacientes.append(paciente)
    return pacientes

# 🔹 6. Médicos sin pacientes
def medicos_sin_pacientes():
    driver = get_driver()
    db = get_mongo_connection()
    query = """
    MATCH (m:Medico)
    WHERE NOT (:Paciente)-[:ATENDIDO_POR]->(m)
    RETURN m.matricula AS matricula_medico
    """
    medicos = []
    with driver.session() as session:
        for record in session.run(query):
            medico = db["medicos"].find_one({"matricula": record["matricula_medico"]}, {"_id":0})
            if medico:
                medicos.append(medico)
    return medicos

# 🔹 7. Pacientes con varios médicos
def pacientes_con_varios_medicos():
    driver = get_driver()
    db = get_mongo_connection()
    query = """
    MATCH (p:Paciente)-[:ATENDIDO_POR]->(m:Medico)
    WITH p, count(m) AS cantidad
    WHERE cantidad > 1
    RETURN p.dni AS dni_paciente, cantidad
    """
    pacientes = []
    with driver.session() as session:
        for record in session.run(query):
            paciente = db["pacientes"].find_one({"dni": record["dni_paciente"]}, {"_id":0})
            if paciente:
                paciente["cantidad_medicos"] = record["cantidad"]
                pacientes.append(paciente)
    return pacientes
