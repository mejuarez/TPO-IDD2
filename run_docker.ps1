# Script para correr todo con Docker
Write-Host "🐳 Iniciando VidaSana con Docker Compose..." -ForegroundColor Cyan

# Verificar si hay procesos Python usando el puerto 8000
$pythonProcess = Get-NetTCPConnection -LocalPort 8000 -ErrorAction SilentlyContinue | 
    Select-Object -ExpandProperty OwningProcess | 
    Get-Process -ErrorAction SilentlyContinue | 
    Where-Object { $_.Name -like "*python*" }

if ($pythonProcess) {
    Write-Host "⚠️  Detectado proceso Python en puerto 8000. Deteniendo..." -ForegroundColor Yellow
    $pythonProcess | Stop-Process -Force
    Start-Sleep -Seconds 2
}

Write-Host "🚀 Levantando contenedores..." -ForegroundColor Green
docker-compose up -d

Write-Host ""
Write-Host "✅ Servicios iniciados:" -ForegroundColor Green
Write-Host "   📡 API: http://localhost:8000" -ForegroundColor Cyan
Write-Host "   📚 Docs: http://localhost:8000/docs" -ForegroundColor Cyan
Write-Host "   🍃 MongoDB: localhost:27017" -ForegroundColor Cyan
Write-Host "   🔴 Redis: localhost:6379" -ForegroundColor Cyan
Write-Host "   🔵 Neo4j: http://localhost:7474" -ForegroundColor Cyan
Write-Host ""
Write-Host "Ver logs de la API: docker logs vidasana_app -f" -ForegroundColor Yellow
Write-Host "Detener servicios: docker-compose down" -ForegroundColor Yellow
