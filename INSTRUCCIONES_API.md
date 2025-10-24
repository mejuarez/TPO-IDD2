# 🏥 VidaSana API - Instrucciones de Uso

## 🚀 Hay 2 formas de correr la API:

---

## Opción 1: Con Docker (RECOMENDADO) ✅

Esta opción corre toda la infraestructura (MongoDB, Redis, Neo4j y la API) en contenedores.

### Iniciar todos los servicios:
```powershell
docker-compose up -d
```

### Ver logs de la API:
```powershell
docker logs vidasana_app -f
```

### Detener todos los servicios:
```powershell
docker-compose down
```

### URL de la API:
- **API**: http://localhost:8000
- **Documentación Swagger**: http://localhost:8000/docs
- **MongoDB**: localhost:27017
- **Redis**: localhost:6379
- **Neo4j Browser**: http://localhost:7474

---

## Opción 2: Desarrollo Local (sin Docker para la API)

Esta opción corre solo las bases de datos en Docker, pero la API localmente en tu máquina.

### 1. Iniciar solo las bases de datos:
```powershell
docker-compose up mongodb redis neo4j -d
```

### 2. Activar entorno virtual (si no está activado):
```powershell
.\.venv\Scripts\Activate.ps1
```

### 3. Correr la API localmente:
```powershell
.\run_api.ps1
```

**O manualmente:**
```powershell
cd c:\Users\cacer\Desktop\vidaSana
$env:PYTHONPATH = "c:\Users\cacer\Desktop\vidaSana"
python -m uvicorn app.api.main:app --host 0.0.0.0 --port 8000 --reload
```

### URL de la API:
- **API**: http://localhost:8000
- **Documentación Swagger**: http://localhost:8000/docs

---

## 📡 Endpoints Disponibles

### General
- `GET /` - Información de la API

### Médicos
- `GET /medicos/` - Listar todos los médicos
- `GET /medicos/{matricula}` - Obtener un médico por matrícula
- `POST /medicos/` - Crear un nuevo médico

### Pacientes
- `GET /pacientes/` - Listar todos los pacientes
- `GET /pacientes/{dni}` - Obtener un paciente por DNI
- `POST /pacientes/` - Crear un nuevo paciente
- `POST /pacientes/{dni}/sintomas` - Agregar síntoma a paciente
- `GET /pacientes/{dni}/diagnostico` - Obtener diagnóstico

### Turnos
- `GET /turnos/` - Listar todos los turnos
- `POST /turnos/` - Crear un nuevo turno

---

## 🔧 Uso con Postman

### Configuración Base:
1. Base URL: `http://localhost:8000`
2. Headers (opcional): `Content-Type: application/json`

### Ejemplos de Requests:

#### Listar médicos:
```
GET http://localhost:8000/medicos/
```

#### Crear un paciente:
```
POST http://localhost:8000/pacientes/
Content-Type: application/json

{
  "dni": "12345678",
  "nombre": "Juan",
  "apellido": "Pérez",
  "email": "juan@mail.com",
  "telefono": "1234567890"
}
```

#### Agregar síntoma:
```
POST http://localhost:8000/pacientes/12345678/sintomas
Content-Type: application/json

{
  "sintoma": "dolor de cabeza"
}
```

---

## ⚠️ Solución de Problemas

### Error: "Socket hang up" en Postman
**Causa**: Dos servicios intentando usar el puerto 8000 simultáneamente.

**Solución**:
1. Elige UNA opción (Docker O local)
2. Si usas Docker: `docker-compose up -d`
3. Si usas local: Para Docker primero con `docker stop vidasana_app`, luego usa `.\run_api.ps1`

### Error: "ModuleNotFoundError: No module named 'fastapi'"
**Solución**:
```powershell
pip install -r requirements.txt
```

### Error: No se puede conectar a MongoDB/Redis/Neo4j
**Solución**: Verifica que los contenedores estén corriendo:
```powershell
docker ps
```

Si no están corriendo:
```powershell
docker-compose up mongodb redis neo4j -d
```

---

## 📦 Dependencias Instaladas

- `fastapi` - Framework web
- `uvicorn[standard]` - Servidor ASGI
- `pymongo` - Cliente de MongoDB
- `redis` - Cliente de Redis
- `neo4j` - Cliente de Neo4j
- `bcrypt` - Encriptación de contraseñas
- `pydantic` - Validación de datos
- `python-dotenv` - Variables de entorno

---

## 🌍 Variables de Entorno

### Desarrollo Local (`.env`):
```env
MONGO_URI=mongodb://localhost:27017/
MONGO_DB=vidasana
REDIS_HOST=localhost
REDIS_PORT=6379
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=neo4jpassword
```

### Docker (configurado en `docker-compose.yml`):
Las variables se configuran automáticamente para usar los nombres de los servicios Docker (mongodb, redis, neo4j).

---

## ✅ Checklist Pre-Desarrollo

- [ ] Contenedores de BD corriendo: `docker ps`
- [ ] Entorno virtual activado (solo para desarrollo local)
- [ ] Dependencias instaladas: `pip list`
- [ ] Puerto 8000 libre: `netstat -ano | findstr :8000`
- [ ] API respondiendo: `curl http://localhost:8000/`

---

¡Listo para desarrollar! 🚀
