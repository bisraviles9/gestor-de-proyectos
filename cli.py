"""Gestor de tareas de proyecto en Python estándar (sin dependencias externas)."""
import argparse
import csv
from datetime import date
from pathlib import Path

FIELDS = ["tarea", "responsable", "inicio", "fin", "progreso", "estado", "prioridad"]
DEFAULT_FILE = Path("tareas_proyecto.csv")


def load(path):
    if not path.exists():
        return []
    with path.open(newline="", encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))


def save(path, tasks):
    with path.open("w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(tasks)


def main():
    parser = argparse.ArgumentParser(description="Administra tareas de un proyecto desde la terminal.")
    parser.add_argument("--archivo", type=Path, default=DEFAULT_FILE, help="CSV donde guardar las tareas")
    commands = parser.add_subparsers(dest="comando", required=True)
    commands.add_parser("listar", help="Muestra todas las tareas")
    add = commands.add_parser("agregar", help="Agrega una tarea")
    add.add_argument("tarea")
    add.add_argument("--responsable", default="Sin asignar")
    add.add_argument("--inicio", default=date.today().isoformat(), help="AAAA-MM-DD")
    add.add_argument("--fin", required=True, help="AAAA-MM-DD")
    add.add_argument("--progreso", type=int, choices=range(101), default=0)
    add.add_argument("--estado", choices=["Pendiente", "En progreso", "Completada"], default="Pendiente")
    add.add_argument("--prioridad", choices=["Alta", "Media", "Baja"], default="Media")
    commands.add_parser("resumen", help="Muestra métricas del proyecto")
    args = parser.parse_args()
    tasks = load(args.archivo)
    if args.comando == "agregar":
        start, end = date.fromisoformat(args.inicio), date.fromisoformat(args.fin)
        if end < start:
            parser.error("La fecha --fin debe ser igual o posterior a --inicio")
        tasks.append({"tarea": args.tarea, "responsable": args.responsable, "inicio": start.isoformat(),
                      "fin": end.isoformat(), "progreso": args.progreso, "estado": args.estado, "prioridad": args.prioridad})
        save(args.archivo, tasks)
        print(f"Tarea guardada en {args.archivo}")
    elif args.comando == "listar":
        if not tasks:
            print("No hay tareas. Agrega una con: python cli.py agregar --help")
        for i, task in enumerate(tasks, 1):
            print(f"{i}. {task['tarea']} | {task['responsable']} | {task['inicio']} → {task['fin']} | {task['progreso']}% | {task['estado']} | prioridad {task['prioridad']}")
    else:
        total = len(tasks)
        done = sum(t.get("estado") == "Completada" for t in tasks)
        active = sum(t.get("estado") == "En progreso" for t in tasks)
        late = sum(t.get("estado") != "Completada" and date.fromisoformat(t["fin"]) < date.today() for t in tasks)
        avg = round(sum(int(t.get("progreso", 0)) for t in tasks) / total) if total else 0
        print(f"Tareas: {total}\nCompletadas: {done}\nEn progreso: {active}\nVencidas: {late}\nAvance promedio: {avg}%")


if __name__ == "__main__":
    main()
