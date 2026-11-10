# Educa Blackboard UCT

## Acceso

La portada `https://educa.blackboard.com/` y `/webapps/login/` devolvían HTTP 508 el 8 de noviembre de 2026, incluso en una petición sin cookies. El acceso institucional SSO sí funcionó:

```
https://educa.blackboard.com/auth-saml/saml/login?apId=_462_1&redirectUrl=https%3A%2F%2Feduca.blackboard.com%2Fultra%2Fcourse
```

No reutilices estados de conversaciones SAML, tickets ni enlaces firmados del historial. Inicia un flujo nuevo con la URL institucional. Comprueba el origen `letmein.blackboard.com`. Firefox puede completar `#user_id` y `#password` con credenciales guardadas. Comprueba solamente si están completos, sin leer ni devolver sus valores, antes de pulsar `#entry-login`. No envíes campos vacíos ni hagas intentos repetidos si el sitio rechaza el acceso.

El control remoto de Firefox aplicaba `signon.autofillForms=false` y `signon.rememberSignons=false`. El perfil personal quedó configurado con autocompletado habilitado y `remote.prefs.recommended=false`, conservando sus preferencias de descarga. No extraigas ni descifres el almacén de contraseñas.

## Consultas autorizadas con la sesión del navegador

La página Ultra tiene un `<base>` que apunta a CloudFront. Por eso `fetch('/learn/api/...')` acaba en el CDN y devuelve XML 404. Construye las peticiones con **`location.origin + ruta`**, nunca con `document.baseURI`.

- Cursos: GET `/learn/api/public/v1/users/me/courses?expand=course&limit=100`.
- Contenidos raíz: GET `/learn/api/public/v1/courses/{curso}/contents?limit=100`.
- Contenidos anidados: GET `/learn/api/public/v1/courses/{curso}/contents/{contenido}/children?limit=100`.
- Adjuntos: GET `/learn/api/public/v1/courses/{curso}/contents/{contenido}/attachments`.

Usa `evaluar` y `fetch` dentro del Firefox del usuario. Comprueba status y JSON. Sigue `paging.nextPage` hasta completar la consulta. Filtra el semestre con `course.courseId` terminado exactamente en `-2026-2` u otro periodo solicitado; distingue inscripciones deshabilitadas. Recorre los contenidos con `hasChildren`, sin iniciar evaluaciones ni modificar cursos. No publiques la lista histórica completa del usuario.

Una guía de aprendizaje institucional suele encontrarse dentro de "Presentación del curso". Busca el título y el nombre original del archivo, incluyendo acentos y variantes. No confundas una guía de ejercicios con el programa del curso cuando se piden las guías de aprendizaje. Registra los cursos sin guía o sin acceso en lugar de inventar archivos.

## Descargas

Guarda por curso, sin sobrescribir archivos existentes, y verifica tamaño y formato real. Usa `descargar` con el enlace del adjunto y una carpeta absoluta; para enlaces de Blackboard que se visualizan en línea puede ser necesario el parámetro oficial `isForcedDownload=true`. Usa una pestaña de trabajo para conservar el listado de cursos.

Enlaza los archivos desde un índice local que indique curso, nombre original y resultado. No guardes cookies, contraseñas ni consultas firmadas temporales en ese índice.

Para repetir una descarga completa por periodo, el script mantiene un manifiesto con SHA-256, distingue plantillas sin completar y omite archivos ya verificados:

```bash
~/.local/share/corvosetup/mcp/firefox-local/bin/python ~/.agents/skills/firefox-local/scripts/blackboard_guias.py --periodo 2026-2 --destino ~/Descargas/Blackboard/2026-2/Guias_de_aprendizaje
```

Selecciona una pestaña ya autenticada, o usa `--context` con su identificador actual. Detecta también la abreviatura `GA INFO ...`. Conserva todas las versiones publicadas y registra cursos sin guía, inscripciones deshabilitadas y documentos con enlaces que necesiten revisión. El índice separa una plantilla institucional sin completar de una guía redactada para el curso.
