from fastapi import FastAPI
from .routes import pacientes, medicos, turnos

app = FastAPI(title="VidaSana API")

app.include_router(pacientes.router)
app.include_router(medicos.router)
app.include_router(turnos.router)

@app.get("/")
def root():
    return {
        "message": "VidaSana API",
        "version": "1.0",
        "endpoints": {
            "docs": "/docs",
            "medicos": "/medicos",
            "pacientes": "/pacientes",
            "turnos": "/turnos"
        }
    }