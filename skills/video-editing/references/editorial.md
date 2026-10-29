# Criterios para mejorar una grabación

## Ritmo y recortes

La prioridad es claridad y continuidad. Una demo técnica necesita tiempo para ver el
resultado; una charla suele admitir más ajuste de pausas y repeticiones. Conserva
la intención, el orden causal, las advertencias y los ejemplos que hacen comprensible
el tema. No inventes una apertura sensacionalista ni cortes matices para acelerar.

`analyze_video.py` marca silencio acústico por debajo de un umbral configurable.
Una pantalla estática con voz puede ser esencial y una espera con música puede ser
espacio muerto. No apliques los intervalos del detector directamente como una EDL.
Revisa una ventana alrededor de cada intervalo; deja como punto de partida 120 a
250 ms de margen alrededor de la voz y ajusta a oído. Una respiración no es un fallo.
Alinea cortes con fotogramas reales de la secuencia, especialmente con 23.976/29.97.

Para saltos de frase considera B-roll relacionado o un acercamiento leve si mejora
la continuidad. No cambies encuadre a cada pocos segundos por regla. Mantén audio
y video vinculados; si haces J/L cuts, verifica explícitamente la sincronía.
Guarda un mapa de segmentos `source_in`, `source_out`, `timeline_in`, `motivo` para
retimar subtítulos y ubicar recursos, usando segundos y la tasa de la secuencia.

## Voz, ruido y mezcla

Mide antes de procesar y escucha fragmentos representativos de voz, silencio y
picos. El análisis devuelve LUFS integrados, rango de sonoridad y pico verdadero
estimado por `loudnorm`; no modifica el archivo. Un archivo sin audio o con solo
silencio no debe convertirse en una medición de voz válida.

- Reduce zumbido o ruido constante solo hasta que dejen de distraer. Un filtro pasa
  altos suave puede ayudar con retumbe; no adelgaces voces graves indiscriminadamente.
- Compresión moderada para diferencias de voz, EQ para inteligibilidad y limitador
  para picos. Evita procesar dos veces un audio ya limpio o normalizado.
- Como punto inicial de entrega hablada estéreo usa aproximadamente -16 LUFS y
  techo de -1 dBTP; adapta el nivel a referencias del canal y al pedido. No presentes
  ese valor como un requisito obligatorio de YouTube. En mono revisa la percepción
  y el canal de reproducción, no copies la ganancia de una mezcla estéreo.
- Música opcional, con licencia, por debajo de la voz y con ducking suave. Conserva
  silencios narrativos cuando tengan sentido. No añadas música por obligación.

Repite medición y escucha en el render final. AAC puede crear picos entre muestras;
si supera el techo, ajusta el limitador y vuelve a medir. Aumentar volumen no repara
clipping ya grabado. Si no hay escucha real disponible, declara esa limitación.

## Imágenes, contexto y subtítulos

Prefiere contenido del repositorio que corresponda al pasaje: esquema de arquitectura
al explicar componentes, captura al mostrar un flujo, resultado real al hablar de
salidas. Respeta marca, licencias y privacidad. No muestres tokens, terminales con
secretos, datos de clientes ni pantallas personales.

Inspecciona cada imagen. Conserva proporciones y evita logos estirados, texto cortado,
recursos desactualizados y capturas que afirmen funciones no implementadas. Para
material externo anota URL, autor y licencia; una imagen generada no es evidencia
fotográfica del proyecto. No descargues recursos al azar solo para llenar huecos.

Subtítulos fieles a la voz, nombres revisados contra el repo, frases legibles y
contraste suficiente. Usa SRT/VTT existente o transcripción verificada con herramientas
disponibles; no inventes la voz faltante. Recalcula tiempos tras cada recorte.

## Exportación y control de calidad

Mantén resolución y frame rate de origen salvo que el destino pida otra cosa. No
subas resolución esperando crear detalle. Para entrega común, H.264 y AAC en MP4;
conserva el proyecto y sus medios para posteriores ajustes. No fuerces SDR sobre
material HDR sin revisar conversión y color. En móviles verifica rotación y VFR.

Comprueba duración y pistas con FFprobe. Decodifica el render completo:

```sh
ffmpeg -v error -xerror -i /ruta/final.mp4 -f null -
python3 <skill>/scripts/analyze_video.py /ruta/final.mp4
```

Compara duración contra el mapa de montaje, escucha principio/final y todas las
uniones, mira fotogramas a ambos lados de cada corte, títulos y subtítulos completos.
Si aparecen offlineMedia, placeholders o errores de decodificación, el render no está
listo. Informa qué revisaste realmente; una prueba sintética no garantiza el material
real de cámara ni todos los efectos de FilmCraft, que sigue en alpha.
