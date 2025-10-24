# Script para detener el contenedor Docker y correr la API localmente
Write-Host "🛑 Deteniendo contenedor Docker de la API..." -ForegroundColor Yellow
docker stop vidasana_app | Out-Null

Write-Host "✅ Contenedor detenido" -ForegroundColor Green
Write-Host "🚀 Iniciando API localmente..." -ForegroundColor Cyan
Write-Host ""

& "$PSScriptRoot\run_api.ps1"
