# Script para correr la API VidaSana
# Asegura que el servidor se levante correctamente

Write-Host "🚀 Iniciando VidaSana API..." -ForegroundColor Green

# Cambiar al directorio raíz del proyecto
Set-Location -Path "$PSScriptRoot"

# Activar entorno virtual
if (-not $env:VIRTUAL_ENV) {
    Write-Host "⚠️  Activando entorno virtual..." -ForegroundColor Yellow
    & "$PSScriptRoot\.venv\Scripts\Activate.ps1"
}

# Configurar PYTHONPATH para que Python encuentre el módulo 'app'
$env:PYTHONPATH = "$PSScriptRoot"

# Correr uvicorn apuntando a app.api.main:app
Write-Host "📡 API corriendo en http://localhost:8000" -ForegroundColor Cyan
Write-Host "📄 Documentación en http://localhost:8000/docs" -ForegroundColor Cyan
Write-Host "🛑 Presiona CTRL+C para detener el servidor" -ForegroundColor Yellow
Write-Host ""

& "$PSScriptRoot\.venv\Scripts\python.exe" -m uvicorn app.api.main:app --host 0.0.0.0 --port 8000 --reload
