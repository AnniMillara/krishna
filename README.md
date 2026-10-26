# Nido de Peluches

Aplicación web para donar y adoptar peluches, desarrollada con Flask, Jinja2, Bootstrap 5 y MySQL. Incluye registro e inicio de sesión, publicación y edición de donaciones, detalle de peluches, adopción de otros usuarios y contadores de donaciones y visitas.

## Requisitos

- Python 3.10 o superior.
- MySQL Server en ejecución.
- `pip`.

## Instalación en Windows

1. Abre CMD o PowerShell y entra en la carpeta `nido_peluches`.
2. Crea y activa un entorno virtual:

   ```bat
   python -m venv .venv
   .venv\Scripts\activate
   ```

3. Instala las dependencias:

   ```bat
   python -m pip install -r requirements.txt
   ```

4. Copia `.env.example` como `.env` y reemplaza los valores por la configuración de tu MySQL. `SECRET_KEY` debe ser una cadena aleatoria larga y privada (al menos 32 caracteres). No compartas ni subas `.env` al repositorio.
5. Ejecuta el contenido de `esquema.sql` en MySQL Workbench o en la consola de MySQL.
6. Inicia la aplicación:

   ```bat
   python server.py
   ```

7. Abre `http://127.0.0.1:5000` en el navegador.

## Configuración de ejemplo

```env
DB_HOST=localhost
DB_PORT=3306
DB_USER=tu_usuario
DB_PASSWORD=tu_contraseña
DB_NAME=nido_peluches
SECRET_KEY=una_clave_aleatoria_larga_y_privada
```

## Estructura

- `server.py`: configuración de Flask y registro de rutas y errores.
- `db.py`: conexión a MySQL y excepción controlada para errores de base de datos.
- `extensions.py`: instancias de Bcrypt y CSRFProtect.
- `models/`: consultas y operaciones de persistencia.
- `controllers/`: rutas, validaciones y control de acceso.
- `templates/`: vistas Jinja2 con diseño adaptable de Bootstrap.
- `esquema.sql`: creación de la base de datos y sus tablas.

## Funcionalidades

- Registro e inicio de sesión con contraseñas hasheadas mediante Bcrypt.
- Validaciones de datos en el servidor.
- Sesión protegida y formularios con tokens CSRF.
- Publicación, consulta y edición de peluches; solo la persona donante puede editar su publicación.
- Adopción de peluches de otras personas, con una actualización condicional para impedir que dos usuarios adopten simultáneamente el mismo registro.
- Visualización del nombre del adoptante y del estado de adopción.
- Contador de donaciones propias y contador de visitas que no suma las visitas de la persona donante.
- Mensajes de error controlados sin mostrar detalles internos de MySQL.

## Consideraciones de seguridad

- Bcrypt acepta un máximo de 72 bytes de contraseña; el servidor rechaza entradas que superen ese límite y no las trunca silenciosamente.
- Las operaciones que cambian datos usan POST y protección CSRF.
- La clave de sesión se lee desde `.env`; la aplicación no inicia si falta o es demasiado corta.
- Los parámetros de SQL se envían por separado de las consultas para evitar concatenar datos del usuario.
- Configura `COOKIE_SECURE=true` solo cuando la aplicación esté servida mediante HTTPS. En desarrollo local se mantiene `false`.

## Verificación

Se ha realizado una comprobación estática de sintaxis de Python y coherencia de rutas/plantillas en el paquete. No se afirma que las operaciones de registro, login o persistencia hayan sido probadas contra un servidor MySQL real: esas pruebas requieren configurar la base de datos y ejecutarlas en el equipo de entrega.
