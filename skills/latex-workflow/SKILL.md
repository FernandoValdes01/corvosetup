---
name: latex-workflow
description: Crea o modifica informes, documentos, presentaciones y PDFs en LaTeX. Se aplica cuando el usuario menciona un archivo .tex, pide hacer o corregir un informe en un proyecto con LaTeX, o solicita cambios en el documento, aunque no escriba .tex. Compila con la imagen Docker blang/latex:ubuntu, verifica el PDF y limpia los archivos auxiliares después de cada edición.
---

# Flujo LaTeX

Use this skill when the user asks to create an informe, documento, presentación or PDF with LaTeX, or to modify an existing `.tex` file. It also applies to short requests such as "haz un informe de esto" when the repository already has LaTeX sources or its established deliverable is a PDF. Do not wait for the user to repeat the compiler instructions.

## Herramienta disponible

La herramienta principal es la imagen Docker `blang/latex:ubuntu`. El host puede no tener `pdflatex` ni `latexmk` instalados. La imagen sí los contiene.

Use el helper incluido en esta skill desde la raíz del proyecto:

```bash
@HOME@/.codex/skills/latex-workflow/scripts/compile_latex.sh docs/main.tex
```

El helper monta el proyecto en `/work`, conserva el usuario y grupo del host, ejecuta `latexmk` dentro del contenedor, confirma que el PDF exista y ejecuta `latexmk -c` al final. Si el proyecto usa otra ruta, sustituya `docs/main.tex` por su archivo de entrada.

La orden equivalente, cuando sea necesario ejecutarla manualmente, es:

```bash
docker run --rm --user "$(id -u):$(id -g)" \
  -v "$PWD":/work -w /work/docs \
  blang/latex:ubuntu \
  latexmk -pdf -interaction=nonstopmode -halt-on-error -file-line-error main.tex
```

Adapte el directorio de trabajo y el nombre del archivo. Si existe `latexmkrc`, respete su configuración.

## Al comenzar

1. Identifique la raíz del proyecto y lea su `README`, `Makefile`, `latexmkrc` y documentación relacionada.
2. Localice el archivo de entrada. Busque el `.tex` que contiene `\documentclass`; no compile a ciegas un archivo incluido con `\input` o `\include`.
3. Revise las fuentes relacionadas: archivos `.bib`, `.cls`, `.sty`, imágenes, tablas generadas y otros archivos que el documento importe.
4. Preserve cambios previos del usuario. No sobrescriba una estructura existente si el proyecto ya tiene una convención para `docs/`, nombres o recursos.
5. Si el usuario pide crear un informe y no existe una fuente, cree el `.tex` en la ubicación coherente con el proyecto y deje claro cuál es el archivo de entrada.

## Durante la edición

Edite el `.tex` y sus recursos necesarios. Una corrección de contenido, formato, referencias, imágenes, tablas, diagramas o saltos de página cuenta como un cambio que requiere compilación.

No dé por terminada ninguna modificación de LaTeX sin ejecutar de nuevo el helper. `latexmk` decide cuántas pasadas necesita para actualizar referencias, índices y bibliografía.

## Compilación y errores

Después de crear el documento y después de cada corrección:

1. Ejecute `compile_latex.sh` sobre el archivo de entrada.
2. Compruebe el código de salida y que el PDF esperado exista y no tenga tamaño cero.
3. Si falla, lea el `.log` antes de limpiar, corrija la causa real y vuelva a compilar. No esconda el error con `-f` ni declare éxito por la mera existencia de un PDF antiguo.
4. Si el cambio afecta composición, diagramas, tablas o imágenes, renderice y revise visualmente las páginas afectadas. Corrija desbordes, contenido cortado, referencias rotas y elementos ilegibles, y vuelva a compilar.
5. No cambie silenciosamente a un compilador del host. Si Docker o la imagen no están disponibles, informe el bloqueo y no instale ni descargue herramientas sin autorización.

## Limpieza y entrega

La última compilación exitosa debe terminar con `latexmk -c`. El resultado normal conserva el `.tex`, el PDF final y los recursos fuente del proyecto, y elimina auxiliares como `.aux`, `.log`, `.out`, `.toc`, `.fls` y `.fdb_latexmk`.

No use `rm -rf` ni borre carpetas completas. No elimine imágenes, `.bib`, `.cls`, `.sty`, fuentes, archivos editables ni el PDF final. Si una herramienta deja un directorio auxiliar específico, elimine solo ese artefacto cuando esté confirmado que fue generado por la compilación.

En la respuesta final indique, de forma breve:

- qué archivo `.tex` se creó o modificó;
- qué herramienta se usó: `blang/latex:ubuntu` con `latexmk`;
- dónde quedó el PDF;
- que la compilación terminó correctamente y los auxiliares fueron limpiados;
- cualquier warning relevante o revisión visual que no haya sido posible hacer.

Nunca diga que el PDF fue recompilado o que los auxiliares fueron eliminados si el comando no terminó con éxito.
