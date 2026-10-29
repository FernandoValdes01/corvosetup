---
name: photo-editing
description: Crea y edita imágenes con PhotoCraft, incluyendo retoque fotográfico, capas, máscaras, fotomontajes e inserción de objetos como un dragón. Actívala automáticamente cuando pidan editar fotos, componer imágenes, cambiar fondos, colocar elementos o trabajar con PhotoCraft. Usa recursos del repo y solicita imágenes de referencia cuando sean necesarias para el resultado. No sustituye la edición de SVG existente, diagramas técnicos ni la edición de video.
---

# Edición de imágenes con PhotoCraft

Usa **PhotoCraft y su MCP nativo `photocraft`** para los documentos, retoque y
composición. Descubre sus comandos reales, trabaja con capas editables y entrega
el resultado comprobado visualmente. Si se necesita crear contenido generativo,
usa la herramienta `image_gen` y la skill `imagegen` cuando estén disponibles;
integra después el recurso en PhotoCraft. No atribuyas generación de imágenes a
PhotoCraft sin comprobar que existe esa capacidad en la versión instalada.

## Resolver los materiales que faltan

Distingue **imagen base**, **objeto para insertar**, **referencia de apariencia** y
**referencia de estilo**. Abre cada imagen antes de decidir cómo usarla. No supongas
que una imagen de referencia autoriza reemplazar la base ni alterar su identidad.

1. Busca primero adjuntos de la conversación y recursos pertinentes del repo del
   trabajo: fotos, logos, capturas, PSD, `.pcraft`, guías de marca y ejemplos. Usa
   búsquedas dirigidas; no recorras fotos personales ni carpetas ajenas al encargo.
2. Si falta una entrada imprescindible, pide **la imagen concreta y su finalidad**.
   Por ejemplo: "Adjunta la foto base y la imagen del dragón que quieres insertar;
   si no tienes una referencia concreta, puedo crear un dragón original". Si ya
   existe la base, pide solo el dragón. Nunca inventes una ruta o un adjunto recibido.
3. Pregunta cuando la referencia cambie materialmente el resultado: "ese dragón"
   sin referente, un producto exacto, mascota, persona, logo, pose o estilo que debe
   coincidir. Formula una pregunta breve y permite adjuntar la imagen o dar su ruta.
   Las herramientas de preguntas que aceptan solo texto no reciben archivos;
   solicita el adjunto mediante el chat normal del cliente.
4. Si el pedido es libre y los datos bastan, actúa. "Crea un dragón rojo original"
   no exige una imagen previa. "Pon un dragón en esta foto" permite crear un recurso
   coherente si no se exige identidad concreta. Puedes consultar una preferencia
   opcional que aporte valor mientras inspeccionas la base; no encadenes preguntas
   de confirmación ni repitas las ya contestadas.
5. Mientras esperas una imagen obligatoria, inspecciona materiales y prepara el
   documento sin ejecutar decisiones que dependan de ella. No trates la falta de
   respuesta como autorización ni sustituyas un objeto exacto por otro inventado.

Consulta [referencias y composición](references/compositing.md) cuando insertes un
objeto, cambies el fondo o combines imágenes. No pidas más material si las referencias
existentes ya resuelven el encargo.

## Editar y comprobar

- Determina qué debe cambiar y qué debe conservarse: identidad, forma, texto exacto,
  encuadre, proporciones, marcas y transparencia. Usa dimensiones y destino del
  pedido; si no se especifican, conserva el tamaño de origen en una edición.
- Consulta [MCP y persistencia](references/photocraft.md) para conectar, descubrir
  comandos y guardar. No copies IDs de ejemplos. Guarda el original intacto y una
  copia de trabajo nueva; utiliza capas, máscaras y ajustes reversibles.
- Genera un recurso faltante con `image_gen` solo cuando corresponda al pedido y
  esté disponible. Pide transparencia para recortes. Conserva la salida elegida en
  la carpeta del proyecto antes de colocarla; no dejes una capa enlazada únicamente
  a un archivo temporal. Si se exige referencia concreta que falta, espera por ella.
- Integra el recurso con escala, perspectiva, orientación, luz, sombras, color,
  profundidad y grano coherentes con la base. Revisa bordes, pelo/alas/transparencia,
  oclusiones y contacto con el suelo; evita halos y sombras contradictorias.
- Revisa previews del documento tras las intervenciones relevantes, y abre también
  el archivo exportado. Compara el conjunto y las zonas editadas al 100%; comprueba
  que no desaparecieron detalles, texto o partes que debían conservarse. Deshaz y
  corrige problemas observados; no declares una revisión visual solo por existir
  un PNG ni confundas reescalar con recuperar detalle perdido.

## Entrega

Entrega la imagen final y el documento editable `.pcraft` o PSD cuando sea compatible
con las capas usadas. Para transparencias conserva PNG u otro formato con alfa;
JPEG requiere aplanado y no conserva transparencia. Guarda recursos referenciados
y su procedencia. Informa brevemente los cambios, los archivos y las limitaciones
reales de compatibilidad o revisión. No exportes sobre originales.

Si falta una herramienta generativa, dilo y ofrece usar una imagen aportada por el
usuario. No instales modelos, solicites claves ni uses APIs de pago como sustitución
silenciosa. El encargo no autoriza publicar imágenes ni enviar archivos privados a
servicios externos ajenos al flujo solicitado.
