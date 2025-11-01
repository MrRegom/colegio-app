@echo off
chcp 65001 >nul
echo ========================================
echo   VERIFICACION COMPLETA DEL SISTEMA
echo ========================================
echo.

echo Ejecutando verificacion...
python verificar_y_actualizar.py

echo.
echo ========================================
echo   VERIFICACION COMPLETADA
echo ========================================
echo.
echo Revisa el archivo: reporte_verificacion.txt
echo.
pause

