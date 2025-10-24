from pymongo import MongoClient

def agregar_campos_pacientes():
    # Conexión al contenedor de Mongo (ajustá la URI si tu servicio se llama distinto en docker-compose)
    client = MongoClient("mongodb://mongodb:27017/")
    db = client["vidasana"]  # Cambiá por el nombre de tu base
    pacientes = db["pacientes"]

    # Actualiza todos los documentos agregando los campos vacíos si no existen
    resultado = pacientes.update_many(
        {},
        {
            "$set": {
                "mayor_frecuencia_cardiaca_dia": [],
                "sintomas_diarios": []
            }
        }
    )

    print(f"✅ Campos agregados correctamente a {resultado.modified_count} pacientes.")
if __name__ == "__main__":
    agregar_campos_pacientes()