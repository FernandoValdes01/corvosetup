#!/usr/bin/env bash
set -Eeuo pipefail

image="${LATEX_DOCKER_IMAGE:-blang/latex:ubuntu}"

usage() {
  printf 'Uso: %s ruta/al/archivo.tex\n' "$(basename "$0")" >&2
}

if [[ $# -ne 1 ]]; then
  usage
  exit 2
fi

source_input="$1"
if [[ ! -f "$source_input" ]]; then
  printf 'No existe el archivo fuente: %s\n' "$source_input" >&2
  exit 2
fi

if command -v docker >/dev/null 2>&1; then
  runtime=(docker)
elif command -v podman >/dev/null 2>&1; then
  runtime=(podman)
else
  printf 'No se encontró Docker ni Podman para ejecutar %s\n' "$image" >&2
  exit 127
fi

if ! "${runtime[@]}" image inspect "$image" >/dev/null 2>&1; then
  printf 'La imagen %s no está disponible localmente.\n' "$image" >&2
  printf 'No se descargó automáticamente. Verifique la instalación antes de continuar.\n' >&2
  exit 125
fi

project_root="$(pwd -P)"
if git_root="$(git rev-parse --show-toplevel 2>/dev/null)"; then
  project_root="$(cd "$git_root" && pwd -P)"
fi

source_abs="$(realpath "$source_input")"
case "$source_abs" in
  "$project_root"/*)
    source_rel="${source_abs#"$project_root"/}"
    ;;
  *)
    printf 'El archivo fuente debe estar dentro de la raíz del proyecto: %s\n' "$project_root" >&2
    exit 2
    ;;
esac

source_dir="$(dirname "$source_rel")"
source_name="$(basename "$source_rel")"
if [[ "$source_dir" == "." ]]; then
  container_workdir=/work
else
  container_workdir="/work/$source_dir"
fi

container_args=(
  run --rm
  --user "$(id -u):$(id -g)"
  -v "$project_root:/work"
  -w "$container_workdir"
  "$image"
)

printf 'Compilando %s con %s y latexmk...\n' "$source_rel" "$image"
"${runtime[@]}" "${container_args[@]}" \
  latexmk -pdf -interaction=nonstopmode -halt-on-error -file-line-error "$source_name"

pdf_abs="${source_abs%.tex}.pdf"
if [[ ! -s "$pdf_abs" ]]; then
  printf 'La compilación terminó, pero no se encontró un PDF válido: %s\n' "$pdf_abs" >&2
  exit 1
fi

printf 'Limpiando archivos auxiliares de LaTeX...\n'
"${runtime[@]}" "${container_args[@]}" latexmk -c "$source_name"

if [[ ! -s "$pdf_abs" ]]; then
  printf 'La limpieza eliminó o dejó inválido el PDF esperado: %s\n' "$pdf_abs" >&2
  exit 1
fi

printf 'Listo: %s\n' "${pdf_abs#"$project_root"/}"
