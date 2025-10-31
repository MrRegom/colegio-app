@echo off
chcp 65001 >nul
echo ========================================
echo   SUBIENDO CAMBIOS A GIT
echo ========================================
echo.
echo Directorio actual:
cd
echo.
echo Cambiando a directorio del proyecto...
cd /d "c:\Users\mr.yo\Downloads\colegioapp\colegio"
echo.
echo [1/4] Verificando estado de Git...
git status
echo.
echo [2/4] Agregando todos los archivos...
git add -A
if %ERRORLEVEL% NEQ 0 (
    echo ERROR al agregar archivos!
    pause
    exit /b 1
)
echo Archivos agregados correctamente.
echo.
echo [3/4] Creando commit...
git commit -m "avance inventario y sus gestores"
if %ERRORLEVEL% NEQ 0 (
    echo ERROR al crear commit!
    pause
    exit /b 1
)
echo Commit creado correctamente.
echo.
echo [4/4] Subiendo a repositorio remoto...
git push
if %ERRORLEVEL% NEQ 0 (
    echo ERROR al subir cambios!
    pause
    exit /b 1
)
echo.
echo ========================================
echo   PROCESO COMPLETADO EXITOSAMENTE
echo ========================================
echo.
echo Verificando estado final...
git status
echo.
pause

