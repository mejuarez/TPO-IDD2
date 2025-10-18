from pymongo import MongoClient

def get_mongo_connection(uri="mongodb://localhost:27017/", db_name="vidasana"):
    try:
        client = MongoClient(uri)
        db = client[db_name]
        print("✅ Conectado a MongoDB")
        return db
    except Exception as e:
        print("❌ Error conectando a MongoDB:", e)
        return None