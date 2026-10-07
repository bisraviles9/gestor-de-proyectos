import csv
import html
import io
from datetime import date, timedelta

import streamlit as st

st.set_page_config(page_title="Gestor de proyectos", page_icon="📊", layout="wide")

FIELDS = ["tarea", "responsable", "inicio", "fin", "progreso", "estado", "prioridad"]
SAMPLE = [
    {"tarea": "Definir alcance y objetivos", "responsable": "Ana", "inicio": "2026-10-01", "fin": "2026-10-04", "progreso": 100, "estado": "Completada", "prioridad": "Alta"},
    {"tarea": "Investigar usuarios", "responsable": "Luis", "inicio": "2026-10-03", "fin": "2026-10-10", "progreso": 75, "estado": "En progreso", "prioridad": "Alta"},
    {"tarea": "Diseñar prototipo", "responsable": "Marta", "inicio": "2026-10-08", "fin": "2026-10-16", "progreso": 40, "estado": "En progreso", "prioridad": "Media"},
    {"tarea": "Desarrollar versión inicial", "responsable": "Bryan", "inicio": "2026-10-14", "fin": "2026-10-26", "progreso": 10, "estado": "Pendiente", "prioridad": "Alta"},
    {"tarea": "Pruebas y correcciones", "responsable": "Luis", "inicio": "2026-10-24", "fin": "2026-10-30", "progreso": 0, "estado": "Pendiente", "prioridad": "Media"},
    {"tarea": "Entrega del proyecto", "responsable": "Bryan", "inicio": "2026-10-31", "fin": "2026-11-02", "progreso": 0, "estado": "Pendiente", "prioridad": "Alta"},
]


def normalize(rows):
    cleaned = []
    for row in rows:
        try:
            start = date.fromisoformat(str(row["inicio"])[:10])
            end = date.fromisoformat(str(row["fin"])[:10])
            progress = max(0, min(100, int(float(row.get("progreso", 0)))))
            status = str(row.get("estado", "Pendiente"))
            if status not in ("Pendiente", "En progreso", "Completada"):
                status = "Pendiente"
            priority = str(row.get("prioridad", "Media"))
            if priority not in ("Alta", "Media", "Baja"):
                priority = "Media"
            if end < start:
                continue
            cleaned.append({"tarea": str(row.get("tarea", "Tarea sin nombre")),
                            "responsable": str(row.get("responsable", "Sin asignar")),
                            "inicio": start.isoformat(), "fin": end.isoformat(),
                            "progreso": progress, "estado": status, "prioridad": priority})
        except (ValueError, TypeError, KeyError):
            continue
    return cleaned


def csv_bytes(rows):
    out = io.StringIO(newline="")
    writer = csv.DictWriter(out, fieldnames=FIELDS)
    writer.writeheader()
    writer.writerows(rows)
    return out.getvalue().encode("utf-8-sig")


if "tasks" not in st.session_state:
    st.session_state.tasks = SAMPLE.copy()

st.title("📊 Gestor de proyectos")
st.caption("Organiza tareas, responsables, fechas y avance en un solo lugar.")

with st.sidebar:
    st.header("Datos del proyecto")
    uploaded = st.file_uploader("Cargar tareas desde CSV", type=["csv"])
    if uploaded is not None:
        try:
            text = uploaded.getvalue().decode("utf-8-sig")
            st.session_state.tasks = normalize(list(csv.DictReader(io.StringIO(text))))
            st.success(f"Se cargaron {len(st.session_state.tasks)} tareas.")
        except Exception:
            st.error("No pude leer el CSV. Revisa que tenga las columnas del ejemplo.")
    if st.button("Restaurar datos de ejemplo", use_container_width=True):
        st.session_state.tasks = SAMPLE.copy()
        st.rerun()
    st.download_button("Descargar tareas CSV", data=csv_bytes(st.session_state.tasks),
                       file_name="tareas_proyecto.csv", mime="text/csv", use_container_width=True)

with st.expander("➕ Agregar una tarea", expanded=False):
    with st.form("new_task", clear_on_submit=True):
        c1, c2 = st.columns(2)
        name = c1.text_input("Nombre de la tarea")
        owner = c2.text_input("Responsable", value="Sin asignar")
        c3, c4 = st.columns(2)
        start = c3.date_input("Fecha de inicio", value=date.today())
        due = c4.date_input("Fecha de fin", value=date.today() + timedelta(days=7))
        c5, c6, c7 = st.columns(3)
        progress = c5.slider("Avance (%)", 0, 100, 0)
        status = c6.selectbox("Estado", ["Pendiente", "En progreso", "Completada"])
        priority = c7.selectbox("Prioridad", ["Alta", "Media", "Baja"])
        if st.form_submit_button("Agregar tarea", type="primary"):
            if not name.strip():
                st.error("Escribe el nombre de la tarea.")
            elif due < start:
                st.error("La fecha de fin debe ser igual o posterior al inicio.")
            else:
                st.session_state.tasks.append({"tarea": name.strip(), "responsable": owner.strip() or "Sin asignar",
                    "inicio": start.isoformat(), "fin": due.isoformat(), "progreso": progress,
                    "estado": status, "prioridad": priority})
                st.rerun()

tasks = st.session_state.tasks
if not tasks:
    st.info("Todavía no hay tareas. Agrega una o carga un archivo CSV.")
    st.stop()

f1, f2 = st.columns(2)
status_filter = f1.multiselect("Filtrar por estado", ["Pendiente", "En progreso", "Completada"], default=["Pendiente", "En progreso", "Completada"])
people = sorted({r["responsable"] for r in tasks})
owner_filter = f2.multiselect("Filtrar por responsable", people, default=people)
shown = [r for r in tasks if r["estado"] in status_filter and r["responsable"] in owner_filter]

complete = sum(r["estado"] == "Completada" for r in tasks)
in_progress = sum(r["estado"] == "En progreso" for r in tasks)
late = sum(r["estado"] != "Completada" and date.fromisoformat(r["fin"]) < date.today() for r in tasks)
avg = round(sum(int(r["progreso"]) for r in tasks) / len(tasks)) if tasks else 0
m1, m2, m3, m4 = st.columns(4)
m1.metric("Tareas", len(tasks))
m2.metric("Completadas", complete)
m3.metric("En progreso", in_progress)
m4.metric("Vencidas", late)
st.progress(avg / 100, text=f"Avance promedio del proyecto: {avg}%")

st.subheader("Plan de trabajo")
if shown:
    min_day = min(date.fromisoformat(r["inicio"]) for r in shown)
    max_day = max(date.fromisoformat(r["fin"]) for r in shown)
    span = max((max_day - min_day).days + 1, 1)
    colors = {"Completada": "#16a34a", "En progreso": "#2563eb", "Pendiente": "#f59e0b"}
    bits = ["<div style='overflow-x:auto'>"]
    for task in sorted(shown, key=lambda x: x["inicio"]):
        begin = date.fromisoformat(task["inicio"])
        finish = date.fromisoformat(task["fin"])
        left = (begin - min_day).days / span * 100
        width = max((finish - begin).days + 1, 1) / span * 100
        name_safe = html.escape(task["tarea"])
        owner_safe = html.escape(task["responsable"])
        color = colors[task["estado"]]
        bits.append(f"<div style='display:grid;grid-template-columns:190px 1fr;gap:12px;align-items:center;margin:10px 0'>"
                    f"<div style='font-size:13px'><b>{name_safe}</b><br><span style='color:#777'>{owner_safe}</span></div>"
                    f"<div style='height:28px;background:repeating-linear-gradient(90deg,#f1f5f9 0,#f1f5f9 calc(10% - 1px),#dbe2ea calc(10% - 1px),#dbe2ea 10%);border-radius:6px;position:relative'>"
                    f"<div title='{task['progreso']}% · {task['estado']}' style='position:absolute;left:{left:.2f}%;width:{width:.2f}%;height:100%;min-width:7px;border-radius:6px;background:{color};opacity:.88'></div></div></div>")
    bits.append(f"<div style='margin-left:202px;color:#666;font-size:12px'>{min_day.strftime('%d %b %Y')} — {max_day.strftime('%d %b %Y')}</div></div>")
    st.markdown("".join(bits), unsafe_allow_html=True)
else:
    st.info("No hay tareas que coincidan con esos filtros.")

st.subheader("Detalle de tareas")
if shown:
    st.dataframe([{**r, "progreso": f"{r['progreso']}%"} for r in shown], use_container_width=True, hide_index=True)
    remove_name = st.selectbox("Eliminar una tarea (opcional)", ["— No eliminar —"] + [r["tarea"] for r in tasks])
    if remove_name != "— No eliminar —" and st.button("Eliminar tarea seleccionada"):
        idx = next((i for i, r in enumerate(tasks) if r["tarea"] == remove_name), None)
        if idx is not None:
            tasks.pop(idx)
            st.rerun()

st.caption("Los datos se guardan durante la sesión. Descarga el CSV para conservarlos o volver a cargarlos después.")
