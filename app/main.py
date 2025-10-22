from medico import crear_medico, existe_medico, obtener_medico_por_matricula
from paciente import crear_paciente, existe_paciente
from consultas import (
    obtener_paciente_por_dni, obtener_pacientes_por_tipo_sangre,
    obtener_pacientes_por_medico, obtener_medicos_por_especialidad
)
from utils import limpiar_paciente, limpiar_medico, limpiar_lista

from conex_mongo import get_mongo_connection
from turno import registrar_turno, obtener_turnos, obtener_recordatorios
from redis import Redis
from pymongo.errors import DuplicateKeyError
from datetime import datetime
import random

# ---------------------------
# Conexiones
# ---------------------------
print("Conectando a MongoDB...")
db = get_mongo_connection()
print("✅ Conectado a MongoDB")

# Conexión Redis
try:
    redis_client = Redis(host="localhost", port=6379, db=0, decode_responses=True)
    redis_client.ping()
    print("✅ Conectado a Redis correctamente.")
except Exception as e:
    print(f"❌ Error al conectar a Redis: {e}")
    redis_client = None

if redis_client:
    redis_client.flushdb()  # limpiar Redis al inicio para pruebas

# ---------------------------
# Médicos a crear
# ---------------------------
medicos_a_crear = [
    {"matricula": "M001", "username": "juanperez", "password": "123456", "especialidad": "Cardiología", "email": "juan@mail.com"},
    {"matricula": "M002", "username": "mariagarcia", "password": "abcdef", "especialidad": "Pediatría", "email": "maria@mail.com"},
    {"matricula": "M003", "username": "pedrosanchez", "password": "qwerty", "especialidad": "Neurología", "email": "pedro@mail.com"}
]

medico_ids = {}
for m in medicos_a_crear:
    if not existe_medico(m["matricula"]):
        resultado = crear_medico(m["matricula"], m["username"], m["password"], m["especialidad"], m["email"])
        print(f"Médico {m['username']}: {resultado}")
    medico_doc = obtener_medico_por_matricula(m["matricula"])
    if medico_doc:
        medico_ids[m["matricula"]] = medico_doc["_id"]

# ---------------------------
# Pacientes a crear
# ---------------------------
pacientes_a_crear = [
    {"dni": "12345678", "nombre": "Lucas Caceres", "fecha_nacimiento": "1998-03-15", "email": "lucas@mail.com", "telefono": "+54 911 1111-1111", "tipo_de_sangre": "A+", "medico_id": "M001"},
    {"dni": "87654321", "nombre": "Ana Lopez", "fecha_nacimiento": "1985-07-22", "email": "ana@mail.com", "telefono": "+54 911 2222-2222", "tipo_de_sangre": "O-", "medico_id": "M002"},
    {"dni": "11223344", "nombre": "Pedro Martínez", "fecha_nacimiento": "1990-12-10", "email": "pedro@mail.com", "telefono": "+54 911 3333-3333", "tipo_de_sangre": "B+", "medico_id": "M003"},
    {"dni": "44332211", "nombre": "Laura Gómez", "fecha_nacimiento": "1995-05-05", "email": "laura@mail.com", "telefono": "+54 911 4444-4444", "tipo_de_sangre": "AB+", "medico_id": "M001"},
    {"dni": "55667788", "nombre": "Carlos Ruiz", "fecha_nacimiento": "1988-08-18", "email": "carlos@mail.com", "telefono": "+54 911 5555-5555", "tipo_de_sangre": "O+", "medico_id": "M002"}
]

for p in pacientes_a_crear:
    if not existe_paciente(p["dni"]):
        resultado = crear_paciente(
            p["nombre"], p["dni"], p["fecha_nacimiento"], p["email"],
            p["telefono"], p["tipo_de_sangre"], medico_ids[p["medico_id"]]
        )
        print(f"Paciente {p['nombre']}: {resultado}")

# ---------------------------
# Configurar colección turnos
# ---------------------------
db.turnos.delete_many({})
print("🧹 Colección 'turnos' limpiada para pruebas.")

try:
    db.turnos.create_index(
        [("id_paciente", 1), ("id_medico", 1), ("fecha_hora", 1)],
        unique=True
    )
    print("🔑 Índice único creado sobre (id_paciente, id_medico, fecha_hora)")
except DuplicateKeyError:
    print("⚠️ El índice único ya existía, continuando...")

# ---------------------------
# Registrar turnos aleatorios
# ---------------------------
print("\n--- REGISTRO DE TURNOS ---")
for _ in range(4):
    registrar_turno(db, redis_client)

# ---------------------------
# Consultas de turnos y recordatorios
# ---------------------------
print("\n--- Turnos en MongoDB ---")
obtener_turnos(db)

recordatorios = obtener_recordatorios(redis_client)
print("\n--- Recordatorios activos en Redis ---")
for r in recordatorios:
    print(f"{r['clave']} -> {r['mensaje']} (TTL: {r['ttl_segundos']} seg)")

# ---------------------------
# Consultas originales
# ---------------------------
print("\n--- Consultas ---\n")

# Buscar paciente por DNI
pac = limpiar_paciente(obtener_paciente_por_dni("12345678"))
print("Paciente con DNI 12345678:", pac)

pacientes_o_neg = limpiar_lista(obtener_pacientes_por_tipo_sangre("O-"), "paciente")
print("Pacientes con tipo de sangre O-:", pacientes_o_neg)

pacientes_doc = limpiar_lista(obtener_pacientes_por_medico(medico_ids["M001"]), "paciente")
print(f"Pacientes del médico M001:", pacientes_doc)

medico = limpiar_medico(obtener_medico_por_matricula("M001"))
print("Médico con matrícula M001:", medico)

cardiologos = limpiar_lista(obtener_medicos_por_especialidad("Cardiología"), "medico")
print("Médicos especialistas en Cardiología:", cardiologos)

print("\n🏁 Fin de ejecución.")
