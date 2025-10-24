FROM python:3.11-slim

# Establecer el directorio de trabajo en /app
WORKDIR /app

# Copiar todo el contenido de la carpeta app al contenedor
COPY . /app

# Instalar todas las dependencias necesarias
RUN pip install --no-cache-dir fastapi uvicorn[standard] pymongo redis python-dotenv bcrypt neo4j dnspython pydantic

EXPOSE 8000

# Ejecutar uvicorn desde /app con la ruta correcta al módulo
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]