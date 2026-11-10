# Firefox personal

La implementación usa WebDriver BiDi en `127.0.0.1:9222` y el perfil habitual. No inicia ni cierra Firefox automáticamente.

Con Firefox cerrado, se puede habilitar el control con:

```bash
firefox --remote-debugging-port 9222
```

El perfil personal usa `remote.prefs.recommended=false` para evitar los cambios de un perfil de pruebas, incluidos la desactivación del autocompletado y de las preferencias de seguridad. El puerto concede control a procesos locales; abrir Firefox sin la opción deshabilita el puerto.

`server.py` sirve MCP por stdio. Todos los clientes utilizan un controlador local único con un socket Unix privado en `/run/user/<uid>/firefox-local/control.sock`, o `~/.local/state/firefox-local` si no existe el directorio de sesión del sistema. No depende de que el cliente MCP herede las variables de la sesión gráfica. Así evita crear sesiones BiDi incompatibles y mantiene estables los contextos entre llamadas.

Herramientas: `pestanas`, `abrir`, `navegar`, `leer`, `evaluar`, `hacer_clic`, `escribir`, `tecla`, `accion_pestana`, `captura`, `atajos`, `abrir_atajo`, `descargar`. Los clics y la escritura utilizan eventos nativos. Los errores del protocolo y de los scripts se propagan. Las descargas requieren confirmación y se guardan sin alterar permanentemente las preferencias del usuario.

El mismo código está disponible como respaldo inmediato si el cliente MCP mantiene una conexión antigua:

```bash
~/.local/share/corvosetup/mcp/firefox-local/bin/python ~/.local/share/corvosetup/mcp/firefox-local/server.py --call '{"tool":"pestanas"}'
```

El controlador solo se inicia al usar una herramienta. Para recargar una actualización de su código, termina **su proceso `server.py --daemon`** normalmente con SIGTERM cuando no haya acciones en curso; cerrará la sesión BiDi sin cerrar Firefox. La siguiente llamada lo inicia de nuevo. Vuelve a listar las pestañas porque sus identificadores cambian. No termines el proceso stdio del cliente MCP.

La skill y la referencia específica de Blackboard están en `skills/firefox-local` (restaurada en `~/.agents/skills/firefox-local`). Las credenciales guardadas se completan en el formulario por el propio Firefox; el controlador no las extrae.

Comprobaciones locales:

```bash
~/.local/share/corvosetup/mcp/firefox-local/bin/python ~/.local/share/corvosetup/mcp/firefox-local/test_server.py
~/.local/share/corvosetup/mcp/firefox-local/bin/python ~/.local/share/corvosetup/mcp/firefox-local/test_integration.py
```

La segunda abre y cierra una pestaña de prueba, hace una descarga temporal desde un servidor HTTP local y verifica los bytes recibidos. No modifica Blackboard.

## Instalación con CorvoSetup

`bash install.sh --only mcp` crea el entorno con `config/mcp/firefox-requirements.txt` en `~/.local/share/corvosetup/mcp/firefox-local`, copia ahí `server.py` y publica el lanzador `~/.local/bin/corvosetup-mcp-firefox-local`. La lista de accesos rápidos verificados y los respaldos locales no forman parte del repositorio.

Las pruebas unitarias del repositorio no necesitan Firefox:

```bash
PYTHONPATH=apps/firefox-mcp python -m unittest discover -s apps/firefox-mcp -p 'test_server.py'
```
