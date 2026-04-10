# RecuperarTusGuijarro

Aplicación de escritorio en Python y Qt para la gestión de usuarios y tareas.

## Entrega 3

Esta entrega incorpora:

- carga dinámica de usuarios en tabla
- filtro por tipo de usuario
- menú `Informes > Listado empleados`
- generación de PDF con el listado de empleados

El informe PDF incluye:

- fecha de impresión
- título `LISTADO DE EMPLEADOS`
- columnas `Nombre`, `Email`, `Móvil` y `Tipo`
- empleados ordenados alfabéticamente por nombre

## Tecnologías

- Python 3.14
- PyQt6
- SQLAlchemy 2.x
- PostgreSQL mediante `psycopg`

## Configuración de base de datos

La aplicación toma la conexión desde la variable de entorno `DATABASE_URL`.

Ejemplo para PostgreSQL en local:

```bash
export DATABASE_URL="postgresql+psycopg://usuario:password@localhost:5432/recuperartusguijarro"
```

Si no se define, el proyecto puede usar la base SQLite local de apoyo `identifier.sqlite`.

## Ejecución

Instalar dependencias:

```bash
uv sync
```

Lanzar la aplicación:

```bash
uv run python main.py
```

## Estructura principal

```text
db/
  connection.py
  models.py
services/
  report_service.py
  tareas_service.py
  usuarios_service.py
templates/
  mainwindow.ui
ui/
  mainwindow.py
events.py
main.py
```

## Flujo de uso para la entrega

1. Abrir la pestaña `Usuarios`.
2. Comprobar que la tabla carga datos de forma dinámica.
3. Seleccionar el filtro `Empleado`.
4. Ir a `Informes > Listado empleados`.
5. Elegir la ruta de guardado del PDF.
6. Verificar que el informe se crea en la carpeta seleccionada.

Por defecto, la ventana de guardado propone una ruta dentro de `informes/`.

## Si editas la interfaz

Si modificas `templates/mainwindow.ui`, recompila la interfaz con:

```bash
pyuic6 templates/mainwindow.ui -o ui/mainwindow.py
```

## Evidencias para la entrega

Capturas recomendadas:

- estructura del proyecto
- historial de commits actualizado
- vista de usuarios con el filtro de empleados
- PDF generado correctamente

Vídeo de 1-2 minutos:

1. mostrar la vista completa de usuarios
2. filtrar por empleados
3. lanzar `Informes > Listado empleados`
4. enseñar el PDF generado

## Preparar `entrega3.zip`

Puedes generar el zip final con el script incluido:

```bash
bash scripts/create_entrega3_zip.sh
```

Si prefieres hacerlo a mano, el comando equivalente es:

```bash
zip -r entrega3.zip . -x ".venv/*" "__pycache__/*" "*/__pycache__/*" ".idea/*" ".git/*" "informes/*" ".claude/*" ".codex/*" "AGENTS.md" "entrega3.zip"
```
