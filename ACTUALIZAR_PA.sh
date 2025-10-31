#!/bin/bash
# Script completo para actualizar PythonAnywhere
# Ejecuta todas las verificaciones y actualizaciones paso a paso

echo "========================================"
echo "ACTUALIZACION PYTHONANYWHERE - INVENTARIO"
echo "========================================"
echo ""

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Función para mostrar paso
mostrar_paso() {
    echo -e "\n${GREEN}[PASO $1]${NC} $2"
    echo "----------------------------------------"
}

# Función para verificar error
verificar_error() {
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓ OK${NC}"
        return 0
    else
        echo -e "${RED}✗ ERROR${NC}"
        return 1
    fi
}

# 1. Verificar directorio
mostrar_paso "1" "Verificando directorio..."
cd ~/colegio-app 2>/dev/null || cd ~/colegio 2>/dev/null || {
    echo -e "${RED}✗ No se encontró el directorio del proyecto${NC}"
    echo "Busca tu directorio con: ls -la"
    exit 1
}
echo "Directorio actual: $(pwd)"
verificar_error

# 2. Activar entorno virtual
mostrar_paso "2" "Activando entorno virtual..."
if [ -d "venv" ]; then
    source venv/bin/activate
elif [ -d "../venv" ]; then
    source ../venv/bin/activate
else
    echo -e "${YELLOW}⚠ Entorno virtual no encontrado, continuando...${NC}"
fi
verificar_error

# 3. Actualizar desde Git
mostrar_paso "3" "Actualizando código desde Git..."
git pull origin main || git pull origin master
verificar_error

# 4. Instalar dependencias
mostrar_paso "4" "Instalando dependencias..."
pip install -r requirements.txt --quiet
verificar_error

# 5. Ejecutar verificación
mostrar_paso "5" "Ejecutando verificación del sistema..."
python verificar_y_actualizar.py
verificar_error

if [ -f "reporte_verificacion.txt" ]; then
    echo -e "\n${GREEN}Reporte generado:${NC}"
    cat reporte_verificacion.txt | tail -20
fi

# 6. Limpiar datos
mostrar_paso "6" "Limpiando datos conflictivos..."
python manage.py shell <<EOF
from django.db import connection
c = connection.cursor()
try:
    c.execute("UPDATE tba_bodega_articulos SET marca_id = NULL WHERE marca_id IS NOT NULL")
    print(f"✓ Limpiados {c.rowcount} artículos")
except Exception as e:
    print(f"⚠ {e}")
try:
    c.execute("UPDATE activo SET marca_id = NULL WHERE marca_id IS NOT NULL")
    print(f"✓ Limpiados {c.rowcount} activos")
except Exception as e:
    print(f"⚠ {e}")
exit()
EOF
verificar_error

# 7. Crear migraciones
mostrar_paso "7" "Creando migraciones..."
python manage.py makemigrations
verificar_error

# 8. Aplicar migraciones
mostrar_paso "8" "Aplicando migraciones..."
python manage.py migrate
verificar_error

# 9. Recopilar estáticos
mostrar_paso "9" "Recopilando archivos estáticos..."
python manage.py collectstatic --noinput
verificar_error

# 10. Verificación final
mostrar_paso "10" "Verificación final..."
python verificar_y_actualizar.py
verificar_error

echo ""
echo "========================================"
echo -e "${GREEN}PROCESO COMPLETADO${NC}"
echo "========================================"
echo ""
echo "IMPORTANTE: Ve al Dashboard → Web → Reload para reiniciar la aplicación"
echo ""
echo "Revisa el reporte completo en: reporte_verificacion.txt"

