# neo_grafos_prueba.py
from conex_neo import get_driver

#  Crear nodo de médico
def crear_medico(nombre, matricula):
    driver = get_driver()
    query = """
    MERGE (m:Medico {matricula: $matricula})
    SET m.nombre = $nombre
    """
    with driver.session() as session:
        session.run(query, nombre=nombre, matricula=matricula)
    print(f"✅ Médico '{nombre}' creado o actualizado en Neo4j.")

#  Crear nodo de paciente
def crear_paciente(nombre, dni):
    driver = get_driver()
    query = """
    MERGE (p:Paciente {dni: $dni})
    SET p.nombre = $nombre
    """
    with driver.session() as session:
        session.run(query, nombre=nombre, dni=dni)
    print(f"✅ Paciente '{nombre}' creado o actualizado en Neo4j.")

#  Crear relación Paciente -> Médico
def relacion_paciente_medico(dni_paciente, matricula_medico):
    driver = get_driver()
    query = """
    MATCH (p:Paciente {dni: $dni})
    MATCH (m:Medico {matricula: $matricula})
    MERGE (p)-[:ATENDIDO_POR]->(m)
    """
    with driver.session() as session:
        session.run(query, dni=dni_paciente, matricula=matricula_medico)
    print(f"🔗 Relación creada: Paciente {dni_paciente} → Médico {matricula_medico}")

#  Limpiar todos los nodos y relaciones (solo para pruebas)
def limpiar_neo4j():
    driver = get_driver()
    query = "MATCH (n) DETACH DELETE n"
    with driver.session() as session:
        session.run(query)
    print("🧹 Neo4j limpio: todos los nodos y relaciones borrados.")
