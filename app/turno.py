# turno.py
from bson import ObjectId
from datetime import datetime
import random

def registrar_turno(db, redis_client):
    """Registra un turno entre un médico y un paciente aleatorios."""
    pacientes = list(db.pacientes.find())
    medicos = list(db.medicos.find())

    if not pacientes or not medicos:
        print("⚠️ No hay médicos o pacientes registrados en la base de datos.")
        return

    paciente = random.choice(pacientes)
    medico = random.choice(medicos)
    fecha_hora = datetime.now()  # guardamos como datetime en Mongo

    # Usar el _id real de Mongo y convertir a string para Redis
    id_paciente = str(paciente["_id"])
    id_medico = str(medico["_id"])

    # Clave única para Redis (por paciente, médico y fecha)
    clave_cache = f"{id_paciente}-{id_medico}-{fecha_hora.strftime('%Y-%m-%d %H:%M:%S')}"

    # Evitar duplicados recientes
    if redis_client.get(clave_cache):
        print("⚠️ Este turno ya fue registrado recientemente (Redis).")
        return

    # Registrar turno en Mongo
    turno = {
        "id_paciente": id_paciente,
        "id_medico": id_medico,
        "fecha_hora": fecha_hora,
        "estado": "pendiente"
    }

    try:
        db.turnos.insert_one(turno)
        redis_client.setex(clave_cache, 30, "registrado")  # cache temporal 30s
        print(f"✅ Turno registrado -> Paciente: {paciente.get('nombre', 'Desconocido')} | Médico: {medico.get('username', 'Desconocido')} | Fecha: {fecha_hora.strftime('%Y-%m-%d %H:%M:%S')}")
    except Exception as e:
        print(f"❌ Error al registrar turno: {e}")


def obtener_turnos(db):
    """Muestra todos los turnos registrados en MongoDB."""
    turnos = db.turnos.find()
    for t in turnos:
        print(f"🗓️ {t['fecha_hora'].strftime('%Y-%m-%d %H:%M:%S')} - Paciente: {t['id_paciente']} | Médico: {t['id_medico']} | Estado: {t['estado']}")


def obtener_recordatorios(redis_client):
    """Obtiene todos los recordatorios activos en Redis."""
    recordatorios = []
    if not redis_client:
        return recordatorios

    for clave in redis_client.keys("*-*-*"):  # patrón para claves de turnos
        mensaje = f"Recordatorio: Turno {clave}"
        ttl = redis_client.ttl(clave)
        recordatorios.append({"clave": clave, "mensaje": mensaje, "ttl_segundos": ttl})
    return recordatorios
