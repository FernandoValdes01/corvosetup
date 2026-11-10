---
name: firefox-local
description: Usa el Firefox personal y su sesión para navegar, usar accesos rápidos, descargar archivos o trabajar con Blackboard. No sustituye las pruebas web habituales cuando no se pide el Firefox personal.
---

# Firefox personal

Trabaja con el perfil habitual mediante `firefox-local`, sin cambiar al navegador de T3 Code ni crear otro perfil. La implementación está en `~/.local/share/corvosetup/mcp/firefox-local/server.py`.

## Conexión y herramientas

Descubre las herramientas disponibles. El controlador local comparte una sola sesión BiDi entre clientes MCP y comandos de respaldo: Firefox solo admite una sesión y los identificadores `context` duran lo que esa sesión. Vuelve a listar `pestanas` después de reiniciar el controlador o Firefox. No abras conexiones WebSocket independientes ni termines procesos MCP para recuperar una conexión.

- `pestanas`: pestañas e iframes, cada uno con su `context`.
- `abrir`, `navegar`, `leer`: devuelve contexto nuevo, navegación y contenido estructurado. `leer` lista controles sin sus valores. Para un iframe usa su propio contexto de `pestanas`.
- `hacer_clic`, `escribir`: puntero y teclado nativos, con comprobación del selector y errores de JavaScript. Verifica el resultado de la acción; no repitas clics ni envíos automáticamente.
- `evaluar`: JavaScript en el contexto, con promesas y devolución JSON. Úsalo para inspección específica y peticiones autorizadas de la página. No muestres contraseñas, cookies ni tokens.
- `captura`: PNG en una ruta absoluta nueva.
- `descargar`: usa la sesión de Firefox y confirma `downloadEnd` y un archivo no vacío. Solo cambia temporalmente la carpeta de descargas; después devuelve a Firefox su comportamiento habitual. No des por descargado un archivo solo porque se hizo clic.

Si el cliente mantiene una versión anterior del MCP, usa la misma implementación por CLI, sin pedir que reinicien la conversación:

```bash
~/.local/share/corvosetup/mcp/firefox-local/bin/python ~/.local/share/corvosetup/mcp/firefox-local/server.py --call '{"tool":"pestanas"}'
```

El argumento es JSON con `tool` y `args`. Para instrucciones con texto o JavaScript extenso importa `server` desde Python y llama sus funciones asíncronas; así evitas escapes de shell. MCP y CLI comparten el mismo controlador y navegador. No hagas `session.new` o `session.end` por fuera del controlador.

## Accesos rápidos y teclado

`atajos(context)` lee nombres y direcciones sin consultas privadas de la página de inicio Tabliss. `abrir_atajo(context,nombre)` abre el nombre exacto conservando internamente su dirección original. Usa los accesos reales del usuario; no inventes sus URLs. Si la pestaña de inicio no está abierta, lee `browser.startup.homepage` del perfil activo y ábrela con la opción de Firefox `--new-tab`, conservando las pestañas existentes.

`accion_pestana` admite `activar`, `cerrar`, `recargar`, `atras` y `adelante`. Para una pestaña nueva usa `abrir`. Son los equivalentes de Ctrl+Tab, Ctrl+W, F5, Alt+izquierda, Alt+derecha y Ctrl+T. `tecla` admite teclas de contenido como `['Escape']`, `['Enter']` y combinaciones como `['Control','f']`; no asumas que controla la barra de dirección ni otros elementos de la interfaz de Firefox.

## Blackboard

Lee [la referencia de Blackboard](references/blackboard.md) para el acceso SSO, el listado de cursos y la descarga de guías.

## Recuperación

Si la conexión falla, vuelve a intentar una lectura una vez. Si no escucha `127.0.0.1:9222`, no cierres ni reinicies una instancia del usuario por tu cuenta. Cuando Firefox esté cerrado y la tarea autorice habilitarlo, puedes abrir el perfil habitual con `firefox --remote-debugging-port 9222`. Si ya está abierto sin el puerto, informa cómo habilitarlo cerrándolo normalmente primero.

En este perfil `user.js` fija `remote.prefs.recommended=false`: el modo de pruebas desactivaba las contraseñas guardadas y alteraba otras preferencias personales. Conserva este ajuste y las preferencias de descarga existentes. No falsifiques `navigator.webdriver` ni el user agent para tratar un `508` sin diagnosticarlo. La indicación de control remoto de Firefox no prueba un bloqueo del sitio.
