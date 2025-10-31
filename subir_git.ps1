Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Subiendo cambios a Git" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "1. Verificando estado..." -ForegroundColor Yellow
git status
Write-Host ""

Write-Host "2. Agregando todos los archivos..." -ForegroundColor Yellow
git add -A
Write-Host ""

Write-Host "3. Creando commit..." -ForegroundColor Yellow
git commit -m "avance inventario y sus gestores"
Write-Host ""

Write-Host "4. Verificando commit..." -ForegroundColor Yellow
git log --oneline -1
Write-Host ""

Write-Host "5. Subiendo a repositorio remoto..." -ForegroundColor Yellow
git push
Write-Host ""

Write-Host "========================================" -ForegroundColor Green
Write-Host "¡Proceso completado!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""

Write-Host "Verificando estado final..." -ForegroundColor Yellow
git status

