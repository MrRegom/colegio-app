# Guía de Git para Principiantes - Paso a Paso

Esta guía te enseñará desde cero cómo subir tu proyecto y trabajar colaborativamente.

## 🎯 Objetivo
Subir tu código a GitHub para que tú y tu compañero puedan trabajar en PythonAnywhere.

---

## PASO 1: Crear una Cuenta en GitHub (si no la tienes)

1. Ve a: https://github.com
2. Haz clic en **"Sign up"** (Registrarse)
3. Completa el formulario con:
   - Username (nombre de usuario)
   - Email
   - Contraseña
4. Verifica tu email

---

## PASO 2: Crear un Nuevo Repositorio en GitHub

1. Una vez dentro de GitHub, haz clic en el botón **"+"** (arriba a la derecha)
2. Selecciona **"New repository"** (Nuevo repositorio)
3. Completa:
   - **Repository name**: `colegio-app` (o el nombre que quieras)
   - **Description**: "Sistema de gestión colegial" (opcional)
   - **Visibilidad**: Selecciona **"Private"** (privado) para mayor seguridad
   - **NO marques** "Add a README file"
   - **NO marques** "Add .gitignore" (ya lo tenemos)
   - **NO marques** "Choose a license"
4. Haz clic en **"Create repository"** (Crear repositorio)

5. **IMPORTANTE**: Copia la URL que aparece. Será algo como:
   ```
   https://github.com/tu-usuario/colegio-app.git
   ```
   O si usas SSH:
   ```
   git@github.com:tu-usuario/colegio-app.git
   ```
   
   **GUARDA ESTA URL**, la necesitarás en el siguiente paso.

---

## PASO 3: Instalar Git en tu Computadora (si no lo tienes)

### Windows:
1. Descarga Git desde: https://git-scm.com/download/win
2. Instala Git (acepta las opciones por defecto)
3. Abre **Git Bash** (busca "Git Bash" en el menú de inicio)
   - O usa PowerShell/CMD

### Verificar que Git esté instalado:
Abre una terminal (PowerShell, CMD o Git Bash) y escribe:
```bash
git --version
```
Si ves un número de versión (ej: `git version 2.x.x`), ¡listo!

---

## PASO 4: Configurar Git (Solo Primera Vez)

En la terminal, ejecuta estos comandos (reemplaza con tus datos reales):

```bash
git config --global user.name "Tu Nombre"
git config --global user.email "tu-email@gmail.com"
```

Ejemplo:
```bash
git config --global user.name "Juan Pérez"
git config --global user.email "juan.perez@gmail.com"
```

---

## PASO 5: Subir tu Proyecto a GitHub

Abre una terminal en la carpeta de tu proyecto:
```bash
cd C:\Users\mr.yo\Downloads\colegioapp\colegio
```

Ahora ejecuta estos comandos **UNO POR UNO**:

### 5.1. Inicializar Git en tu proyecto:
```bash
git init
```
Esto crea un repositorio Git vacío en tu carpeta.

### 5.2. Agregar todos los archivos:
```bash
git add .
```
Esto prepara todos los archivos para subirlos.

### 5.3. Hacer el primer commit (guardar los archivos):
```bash
git commit -m "Primera subida del proyecto"
```
El `-m "mensaje"` es una descripción de lo que estás subiendo.

### 5.4. Conectar con GitHub:
```bash
git remote add origin https://github.com/TU-USUARIO/TU-REPOSITORIO.git
```
**⚠️ IMPORTANTE**: Reemplaza `TU-USUARIO` con tu nombre de usuario de GitHub y `TU-REPOSITORIO` con el nombre que le diste al repositorio.

Ejemplo:
```bash
git remote add origin https://github.com/juanperez/colegio-app.git
```

### 5.5. Subir los archivos:
```bash
git branch -M main
git push -u origin main
```

Te pedirá tus credenciales de GitHub:
- **Username**: Tu usuario de GitHub
- **Password**: Usa un **Personal Access Token** (no tu contraseña normal)

#### Crear Personal Access Token:
1. Ve a GitHub.com
2. Haz clic en tu foto de perfil (arriba derecha)
3. **Settings** (Configuración)
4. En el menú lateral izquierdo: **Developer settings**
5. **Personal access tokens** > **Tokens (classic)**
6. **Generate new token** > **Generate new token (classic)**
7. Dale un nombre: "colegio-app"
8. Selecciona el tiempo de expiración (ej: 90 días)
9. Marca la casilla **"repo"** (esto da permisos para repositorios)
10. Haz clic en **"Generate token"** (al final de la página)
11. **COPIA EL TOKEN** (solo se muestra una vez)
12. Usa ese token como contraseña cuando Git te lo pida

### 5.6. ¡Listo!
Si todo salió bien, verás un mensaje como:
```
Enumerating objects: XX, done.
Writing objects: 100% (XX/XX), done.
```

**Ve a tu repositorio en GitHub y deberías ver todos tus archivos.**

---

## PASO 6: Ver tu App en Línea (PythonAnywhere)

Una vez que el código está en GitHub, necesitas configurarlo en PythonAnywhere.

### 6.1. Crear cuenta en PythonAnywhere:
1. Ve a: https://www.pythonanywhere.com
2. Haz clic en **"Sign up"** (Registrarse)
3. Elige el plan **"Beginner"** (es gratuito)
4. Completa el registro

### 6.2. Configurar el proyecto (primera vez):

1. **Abre una consola Bash**:
   - Ve a la pestaña **"Consoles"** en el dashboard
   - Haz clic en **"Bash"**

2. **Clonar el repositorio**:
```bash
cd ~
git clone https://github.com/TU-USUARIO/TU-REPOSITORIO.git colegio
```
Reemplaza con tu URL real de GitHub.

3. **Crear entorno virtual e instalar dependencias**:
```bash
cd colegio
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

4. **Seguir la guía `QUICK_START_PYTHONANYWHERE.md`** para completar la configuración.

### 6.3. Acceder a tu aplicación:
Una vez configurada, tu app estará disponible en:
```
https://TU-USUARIO.pythonanywhere.com
```

Por ejemplo, si tu usuario es `juanperez`, será:
```
https://juanperez.pythonanywhere.com
```

---

## 🔄 Trabajo Diario - Comandos Esenciales

### Al empezar tu día de trabajo (cada día):

```bash
# 1. Ir a la carpeta del proyecto
cd C:\Users\mr.yo\Downloads\colegioapp\colegio

# 2. Actualizar desde GitHub (obtener los cambios de tu compañero)
git pull origin main
```

### Cuando terminas de trabajar (cada día):

```bash
# 1. Ver qué archivos has cambiado
git status

# 2. Agregar los archivos que quieres guardar
git add .

# 3. Guardar con un mensaje descriptivo
git commit -m "Descripción de lo que cambiaste"

# 4. Subir a GitHub
git push origin main
```

**Ejemplo de mensaje de commit:**
```bash
git commit -m "Agregada funcionalidad de solicitudes de materiales"
git commit -m "Corregido error en el formulario de usuarios"
git commit -m "Actualizado diseño del dashboard"
```

---

## 👥 Cómo Funciona el Trabajo Colaborativo

### Escenario: Tú trabajas hoy, tu compañero mañana

**HOY (Tú):**
1. Al empezar: `git pull` (obtener cambios si hay)
2. Trabajas en tu código
3. Al terminar: `git add .` → `git commit -m "..."` → `git push`

**MAÑANA (Tu Compañero):**
1. Al empezar: `git pull` (obtiene TUS cambios de ayer)
2. Trabaja en su código
3. Al terminar: `git add .` → `git commit -m "..."` → `git push`

**PASADO MAÑANA (Tú otra vez):**
1. Al empezar: `git pull` (obtiene los cambios de tu compañero)
2. Y así sucesivamente...

---

## 🔐 Ticket Explicado - Personal Access Token

**¿Por qué necesito un token?**
GitHub requiere tokens para mayor seguridad. Tu contraseña no funciona directamente.

**¿Cuándo necesito crear uno nuevo?**
- Si expira (después de los días que elegiste)
- Si lo borraste por error
- Si necesitas más permisos

**¿Es seguro?**
Sí, el token es como una contraseña temporal. No lo compartas con nadie.

---

## ❓ Problemas Comunes

### Error: "fatal: remote origin already exists"
```bash
# Solución: Remover el origin y agregarlo de nuevo
git remote remove origin
git remote add origin https://github.com/TU-USUARIO/TU-REPOSITORIO.git
```

### Error: "Authentication failed"
- Verifica que estés usando el Personal Access Token (no tu contraseña)
- Asegúrate de que el token tenga permisos de "repo"

### Error: "Please tell me who you are"
```bash
# Ejecuta esto de nuevo:
git config --global user.name "Tu Nombre"
git config --global user.email "tu-email@gmail.com"
```

### Error: "Updates were rejected"
```bash
# Primero obtプン los cambios más recientes
git pull origin main
# Luego intenta hacer push de nuevo
git push origin main
```

---

## 📋 Resumen de Comandos (Copia y Pega)

### Configuración inicial (una sola vez):
```bash
git config --global user.name "Tu Nombre"
git config --global user.email "tu-email@gmail.com"
cd C:\Users\mr.yo\Downloads\colegioapp\colegio
git init
git add .
git commit -m "Primera subida del proyecto"
git remote add origin https://github.com/TU-USUARIO/TU-REPOSITORIO.git
git branch -M main
git push -u origin main
```

### Trabajo diario:
```bash
# Al empezar
git pull origin main

# Al terminar
git add .
git commit -m "Descripción de los cambios"
git push origin main
```

---

## 🆘 ¿Necesitas Ayuda?

Si tienes problemas:
1. Lee los mensajes de error cuidadosamente
2. Busca en Google el mensaje de error exacto
3. Revisa esta guía de nuevo

**¡Ahora estás listo para subir tu proyecto! 🚀**

