# Script para correr la API desde app/api
# Asegura que el servidor se levante desde la carpeta correcta

Write-Host "🚀 Iniciando VidaSana API desde app/api..." -ForegroundColor Green

# Cambiar al directorio app
Set-Location -Path "$PSScriptRoot\app"

# Verificar que el entorno virtual está activado
if (-not $env:VIRTUAL_ENV) {
    Write-Host "⚠️  Activando entorno virtual..." -ForegroundColor Yellow
    & "$PSScriptRoot\.venv\Scripts\Activate.ps1"
}

# Correr uvicorn apuntando a api.main:app
Write-Host "📡 API corriendo en http://localhost:8000" -ForegroundColor Cyan
Write-Host "📄 Documentación en http://localhost:8000/docs" -ForegroundColor Cyan
uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload
