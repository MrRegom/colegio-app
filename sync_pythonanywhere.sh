#!/bin/bash
# Script para sincronizar cambios del repositorio Git en PythonAnywhere
# Uso: bash sync_pythonanywhere.sh

set -e  # Salir si hay algún error

echo "========================================="
echo "Sincronizacion de PythonAnywhere"
echo "========================================="

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Verificar que estamos en el directorio correcto
if [ ! -f "manage.py" ]; then
    echo -e "${RED}Error: No se encuentra manage.py. Ejecuta este script desde el directorio raiz del proyecto.${NC}"
    exit 1
fi

# Verificar que el entorno virtual existe
if [ ! -d "venv" ]; then
    echo -e "${YELLOW}Advertencia: No se encuentra el entorno virtual. Creando...${NC}"
    python3 -m venv venv
fi

# Activar entorno virtual
echo -e "${GREEN}[1/6]${NC} Activando entorno virtual..."
source venv/bin/activate

# Actualizar desde Git
echo -e "${GREEN}[2/6]${NC} Actualizando desde Git..."
if ! git pull origin main 2>/dev/null; then
    echo -e "${YELLOW}Intentando con 'master'...${NC}"
    git pull origin master || echo -e "${YELLOW}No se pudo actualizar desde Git. Continuando...${NC}"
fi

# Actualizar dependencias
echo -e "${GREEN}[3/6]${NC} Actualizando dependencias..."
pip install --upgrade pip
pip install -r requirements.txt

# Ejecutar migraciones
echo -e "${GREEN}[4/6]${NC} Ejecutando migraciones..."
python manage.py migrate

# Recopilar archivos estáticos
echo -e "${GREEN}[5/6]${NC} Recopilando archivos estáticos..."
python manage.py collectstatic --noinput

# Verificar el sistema
echo -e "${GREEN}[6/6]${NC} Verificando sistema..."
python manage.py check || echo -e "${YELLOW}Advertencia: El check encontró algunos problemas.${NC}"

echo ""
echo -e "${GREEN}=========================================${NC}"
echo -e "${GREEN}Sincronizacion completada!${NC}"
echo -e "${GREEN}=========================================${NC}"
echo ""
echo "IMPORTANTE: Ve a la pestaña 'Web' en PythonAnywhere y haz clic en 'Reload' para aplicar los cambios."
echo ""

