@echo off
chcp 65001 >nul
echo ========================================
echo   ACTUALIZACION COMPLETA
echo ========================================
echo.

echo [1/6] Verificando estado...
python verificar_y_actualizar.py
echo.

echo [2/6] Limpiando datos conflictivos...
python manage.py shell -c "from django.db import connection; c = connection.cursor(); c.execute('UPDATE tba_bodega_articulos SET marca_id = NULL WHERE marca_id IS NOT NULL'); c.execute('UPDATE activo SET marca_id = NULL WHERE marca_id IS NOT NULL'); print('Datos limpiados')"
echo.

echo [3/6] Creando migraciones...
python manage.py makemigrations
echo.

echo [4/6] Aplicando migraciones...
python manage.py migrate
echo.

echo [5/6] Verificando estado final...
python verificar_y_actualizar.py
echo.

echo [6/6] Recopilando archivos estaticos...
python manage.py collectstatic --noinput
echo.

echo ========================================
echo   PROCESO COMPLETADO
echo ========================================
echo.
echo Revisa el archivo: reporte_verificacion.txt
echo.
pause

