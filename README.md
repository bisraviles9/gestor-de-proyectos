# Gestor de proyectos

Tablero de seguimiento inspirado en el ejemplo: tareas, responsables, fechas, avance, estados, prioridades y una vista tipo Gantt.

## Incluye

- `cli.py`: versión de terminal en **Python estándar**, sin paquetes externos.
- `app.py`: interfaz web con Streamlit.
- Importación y descarga CSV para conservar o compartir los datos.
- Datos de muestra que puedes reemplazar.

## Requisitos

- Python 3.9 o superior.
- Para la aplicación web: instalar `requirements.txt`.

## Ejecutar la versión de terminal

```bash
python cli.py listar
python cli.py agregar "Diseñar prototipo" --responsable Ana --inicio 2026-10-07 --fin 2026-10-15 --progreso 20 --estado "En progreso" --prioridad Alta
python cli.py resumen
```

El CSV se crea en `tareas_proyecto.csv`. Para usar otro archivo agrega `--archivo nombre.csv` antes del comando.

## Ejecutar Streamlit

```bash
python -m pip install -r requirements.txt
streamlit run app.py
```

Se abrirá el tablero en el navegador. Los cambios se mantienen mientras la sesión esté activa; descarga el CSV para guardarlos y luego puedes volver a cargarlo.

## CSV

Columnas esperadas: `tarea,responsable,inicio,fin,progreso,estado,prioridad`.

Fechas en formato `AAAA-MM-DD`. Estados: `Pendiente`, `En progreso`, `Completada`. Prioridades: `Alta`, `Media`, `Baja`.

## Publicar en GitHub

Crea un repositorio vacío y desde esta carpeta ejecuta:

```bash
git init
git add .
git commit -m "Añade gestor de proyectos en Python y Streamlit"
git branch -M main
git remote add origin URL_DE_TU_REPOSITORIO
 git push -u origin main
```

No subas datos privados ni credenciales. El proyecto no requiere claves API.
