---
name: video-editing
description: Edita y mejora videos existentes con FilmCraft, con ritmo de YouTube, limpieza de audio y recursos del repositorio. Actívala automáticamente al pedir editar un video, cortar pausas o espacios muertos, mejorar voz, montar una grabación, añadir imágenes de referencia, B-roll, títulos o subtítulos. También para crear un video a partir de clips y material del repo. No se aplica a implementar reproductores web ni a generar únicamente animaciones con código.
---

# Edición de video con FilmCraft

Usa **FilmCraft y su MCP nativo `filmcraft` como editor principal**. Trabaja sobre el
video base y entrega un montaje revisado, no solo instrucciones. FFmpeg/FFprobe son
herramientas auxiliares de análisis, proxies, medición y verificación; no sustituyas
FilmCraft silenciosamente por otro editor. Si falta el MCP, consulta
[el setup y protocolo](references/filmcraft.md) y resuelve el acceso antes de editar.

## Entender el video y aprovechar el repo

- Identifica el archivo base, la audiencia, el propósito y el formato de entrega a
  partir del pedido y del proyecto. Si hay varios videos y no está claro cuál usar,
  pregunta por el base sin detener el inventario de recursos. Para decisiones
  reversibles usa el estilo existente y explica las suposiciones brevemente.
- Busca primero con `rg --files` y búsquedas dirigidas en el repositorio del trabajo:
  README, guion, documentación, slides, diagramas, imágenes, logos, capturas, demos,
  subtítulos y audio. Abre los recursos candidatos antes de usarlos. El repo de la
  skill contiene herramientas; el contenido editorial pertenece al repo del video.
- Usa ese material para entender nombres, conceptos, pasos y hechos que narra la
  grabación. Reutiliza gráficos y capturas cuando expliquen lo que se está diciendo.
  No conviertas automáticamente todo el README en guion ni muestres código ilegible.
- Escucha y revisa el video y una transcripción con tiempos cuando esté disponible.
  Si no puedes reproducir audio o transcribirlo con las herramientas disponibles,
  indícalo: detectar silencio no demuestra que una frase sea prescindible. No
  inventes citas, subtítulos ni contenido supuestamente escuchado.
- Guarda originales intactos y crea una carpeta de entrega nueva. Mantén un registro
  breve de segmentos conservados, descartes y recursos con sus rutas y procedencia.

## Montar como editor de YouTube

Lee [los criterios editoriales](references/editorial.md) para decidir recortes,
audio, imágenes y ritmo según la grabación. Aplica lo que mejora el encargo, sin
rellenar el video con efectos porque estén disponibles.

1. **Diagnóstico.** Ejecuta `python3 <skill>/scripts/analyze_video.py /ruta/base.mp4`
   para medir duración, pistas, silencios candidatos y sonoridad. Comprueba encuadre,
   exposición, foco, legibilidad y sincronía. El análisis es de solo lectura.
2. **Montaje base.** Conserva la apertura útil, la progresión y el cierre. Recorta
   esperas de interfaz, intentos fallidos, repeticiones y espacios muertos que no
   aporten. Contrasta cada candidato de silencio con imagen y voz; conserva pausas
   expresivas, respiración y tiempo para leer o ver una demostración. No cortes
   palabras ni cambies el sentido. Mantén audio y video vinculados. Usa cortes
   limpios, pequeños márgenes y fundidos de audio cuando eviten clics.
3. **Audio.** Prioriza voz inteligible y estable: corrige nivel, ruido constante,
   zumbido y dinámica solo donde hagan falta. Usa EQ, DeNoise, compresión y limitador
   con moderación, descubriendo los parámetros reales del catálogo. Evita voz
   metálica, bombeo y clipping. Baja la música durante la voz. Mide otra vez después
   del procesamiento; no confundas normalización de picos con sonoridad percibida.
4. **Apoyo visual.** Inserta imágenes del repo, B-roll, diagramas o capturas en el
   momento al que corresponden. Usa encuadre, escala y duración legibles, respeta
   proporciones, y deja visibles las acciones que se están explicando. Añade títulos,
   resaltados, acercamientos y subtítulos cuando ayuden a entender. Material externo
   requiere procedencia y permiso de uso adecuado. Si faltan recursos, decide si
   conviene capturar el proyecto o crear una ilustración identificada como tal.
5. **Acabado y revisión.** Corrige color entre tomas sin fingir detalle perdido ni
   hacer upscale por defecto. Ajusta subtítulos a los tiempos del montaje final.
   Revisa imagen y escucha audio en cortes, overlays y transiciones, principio y
   final; comprueba el conjunto completo cuando sea viable. Itera sobre problemas
   observados, guarda `.fcproj`, exporta una copia y valida como indica la referencia.

## Entrega y límites

Entrega el video final, el proyecto editable y un registro de cambios con tiempos de
origen/salida y fuentes visuales. Conserva o empaqueta los medios referenciados para
que el proyecto se pueda abrir después. Incluye SRT/VTT si se crearon subtítulos.
Resume duración antes/después, mejoras aplicadas y resultados reales de validación.

Distingue revisión de fotogramas, medición técnica y escucha real. Si una limitación
impide completar una parte, entrega lo verificado y señala esa parte pendiente.
El pedido de edición no autoriza publicar en YouTube, enviar archivos a terceros,
subir medios privados a servicios de transcripción ni hacer commits del video.
