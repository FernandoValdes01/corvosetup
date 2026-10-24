#!/usr/bin/env python3
"""Instala el visor teach dentro de un proyecto sin tocar su contenido."""

from __future__ import annotations

import argparse
from pathlib import Path
import shutil
import sys


SKILL_ROOT = Path(__file__).resolve().parents[1]
ENGINE = SKILL_ROOT / "assets" / "engine"
LAUNCHER = """#!/usr/bin/env python3
\"\"\"Abre la guía educativa local de este proyecto.\"\"\"
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / ".teach" / "engine"))
from teach import main

if __name__ == "__main__":
    raise SystemExit(main(ROOT, sys.argv[1:]))
"""
GITIGNORE_BEGIN = "# teach-project: artefactos locales de la guía"
GITIGNORE_END = "# fin teach-project"
GITIGNORE_ENTRIES = ("/teach", "/.teach/", "/tutorial.json", "/diagramas/")


def ensure_gitignore(project: Path) -> bool:
    """Agrega o actualiza el bloque gestionado que ignora el material de teach."""
    path = project / ".gitignore"
    if path.exists() and path.is_dir():
        raise SystemExit(f"{path} existe y es un directorio.")
    current = path.read_text(encoding="utf-8") if path.exists() else ""
    block = "\n".join([GITIGNORE_BEGIN, *GITIGNORE_ENTRIES, GITIGNORE_END])
    if GITIGNORE_BEGIN in current:
        start = current.index(GITIGNORE_BEGIN)
        end_marker = current.find(GITIGNORE_END, start + len(GITIGNORE_BEGIN))
        if end_marker == -1:
            updated = current[:start] + block + "\n"
        else:
            updated = current[:start] + block + current[end_marker + len(GITIGNORE_END):]
    else:
        updated = current
        if updated and not updated.endswith("\n"):
            updated += "\n"
        if updated:
            updated += "\n"
        updated += block + "\n"
    if updated == current:
        return False
    path.write_text(updated, encoding="utf-8")
    return True


def install(project: Path) -> None:
    project = project.resolve()
    if not project.is_dir():
        raise SystemExit(f"No existe el directorio del proyecto: {project}")
    if sys.version_info < (3, 11):
        raise SystemExit("teach requiere Python 3.11 o posterior.")
    if not (ENGINE / "teach.py").is_file():
        raise SystemExit(f"Faltan los archivos del motor en {ENGINE}")
    if (project / ".teach").exists() and not (project / ".teach").is_dir():
        raise SystemExit(f"{project / '.teach'} existe y no es un directorio.")
    launcher = project / "teach"
    if launcher.exists() and not launcher.is_file():
        raise SystemExit(f"{launcher} existe y no es un archivo.")

    destination = project / ".teach" / "engine"
    try:
        shutil.copytree(ENGINE, destination, dirs_exist_ok=True)
        shutil.rmtree(destination / "__pycache__", ignore_errors=True)
        launcher.write_text(LAUNCHER, encoding="utf-8")
        launcher.chmod(0o755)
        (project / ".teach" / "state").mkdir(mode=0o700, parents=True, exist_ok=True)
        gitignore_changed = ensure_gitignore(project)
    except OSError as error:
        raise SystemExit(f"No se pudo instalar teach: {error}") from error

    print(f"Motor instalado en {destination}")
    print(f"Lanzador creado en {launcher}")
    print(
        "Artefactos agregados a .gitignore."
        if gitignore_changed
        else "Los artefactos ya estaban ignorados en .gitignore."
    )
    print("Conservados: tutorial.json, diagramas/ y .teach/state/.")


def main() -> int:
    parser = argparse.ArgumentParser(description="Instala la guía teach en un proyecto.")
    parser.add_argument("project", nargs="?", default=".", help="raíz del proyecto (por defecto: actual)")
    args = parser.parse_args()
    install(Path(args.project))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
