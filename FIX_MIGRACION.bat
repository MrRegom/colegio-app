@echo off
echo ========================================
echo   SOLUCION ERROR DE MIGRACION
echo ========================================
echo.
echo Este script limpiara los datos antes de aplicar la migracion.
echo.
echo Paso 1: Abriendo shell de Django para limpiar datos...
python manage.py shell -c "from django.db import connection; cursor = connection.cursor(); cursor.execute('UPDATE tba_bodega_articulos SET marca_id = NULL WHERE marca_id IS NOT NULL'); print('Datos limpiados')"
echo.
echo Paso 2: Aplicando migraciones...
python manage.py migrate
echo.
echo ========================================
echo   PROCESO COMPLETADO
echo ========================================
pause

