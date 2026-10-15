---
name: informe-uct
description: Crea o modifica informes UCT o informes para la Universidad Católica de Temuco usando la plantilla LaTeX personal de Documentos/ramos/BaseInformes. Actívala automáticamente cuando el usuario pida un informe UCT, un informe para la UCT o un informe con su base UCT, aunque no mencione LaTeX ni el nombre de esta skill.
---

# Informes UCT

Usa como fuente de formato `@HOME@/Documentos/ramos/BaseInformes/informe_base.tex` y como logo `@HOME@/Documentos/ramos/BaseInformes/UCT_logo_BN.pdf`. La carpeta real se llama `BaseInformes`, aunque el usuario puede referirse a ella como `Baseinforme`.

## Plantilla y formato

Lee la plantilla vigente al comenzar. Para informes nuevos, copia el `.tex` y el logo al directorio de entrega y trabaja sobre esa copia. Conserva intactos los originales. Si las rutas dejan de existir, busca la carpeta antes de solicitar la plantilla al usuario.

Preserva el formato de la base salvo cambios solicitados por el usuario:

- Clase `article`, tamaño 12 pt, papel A4, márgenes de 2,5 cm y español.
- Interlineado de 1,5 y paquetes de la plantilla.
- Portada centrada con `UCT_logo_BN.pdf` a `0.45\textwidth`, título, profesor, autor, asignatura y fecha, respetando los espacios de la base.
- Datos editables mediante `\TituloInforme`, `\ProfesorInforme`, `\AutorInforme` y `\AsignaturaInforme`.
- Índice en página separada antes del contenido.

Usa Introducción, Marco Teórico, Desarrollo, Conclusión y Bibliografía como estructura inicial. Adapta secciones y subsecciones al encargo o a su rúbrica; no fuerces apartados que no correspondan. Elimina el lorem ipsum, ejemplos, citas y referencias ficticias de la plantilla. Incluye tablas, objetivos y resultados solo cuando el contenido los justifique. Evita duplicar el encabezado Bibliografía al usar `thebibliography`.

## Contenido y entrega

Aprovecha los datos del encargo y del contexto para completar la portada. No inventes profesor, asignatura, autor, resultados ni referencias. Si faltan datos de portada, continúa con el contenido disponible y deja marcadores explícitos para esos campos; pregunta únicamente cuando la información faltante impida desarrollar el informe. Usa la fecha pedida o `\today` si no se especifica otra.

Escribe en español académico claro y sigue las instrucciones de extensión, contenido y citas del usuario. Para editar un informe existente, conserva su contenido y recursos y ajusta el formato al de esta plantilla dentro del alcance pedido.

Guarda el informe en la ubicación indicada por el usuario o en una carpeta coherente con el proyecto o ramo. No guardes entregas nuevas en `BaseInformes` salvo que el usuario lo pida.

Aplica la skill disponible `latex-workflow` de `@HOME@/.codex/skills/latex-workflow/SKILL.md` para compilar con Docker `blang/latex:ubuntu`, revisar visualmente el PDF y limpiar auxiliares. Ejecuta su helper desde la raíz del proyecto:

```bash
@HOME@/.codex/skills/latex-workflow/scripts/compile_latex.sh informe.tex
```

Ajusta la ruta al archivo de entrada. Entrega el `.tex`, el PDF y los recursos necesarios, con enlaces a los archivos. Solo afirma que la compilación y la revisión fueron exitosas si se realizaron; si hay un bloqueo, indica el estado real.
