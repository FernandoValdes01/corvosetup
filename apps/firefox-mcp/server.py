"""Control del Firefox personal mediante una única sesión WebDriver BiDi local."""
import asyncio
import base64
import json
import sys
import os
import functools
import inspect
import signal
import subprocess
import fcntl
from collections import deque
from pathlib import Path
from urllib.parse import urlsplit

from mcp.server.fastmcp import FastMCP
from websockets.asyncio.client import connect
from websockets.exceptions import ConnectionClosed
from websockets.protocol import State

mcp = FastMCP('firefox-local')
_lock = asyncio.Lock()
_ws = None
_sequence = 0
_session_active = False
_daemon_mode = '--daemon' in sys.argv
_runtime_base = Path('/run/user') / str(os.getuid())
if not _runtime_base.is_dir():
    _runtime_base = Path.home() / '.local/state'
_runtime = _runtime_base / 'firefox-local'
_socket = _runtime / 'control.sock'
_rpc_lock = asyncio.Lock()


async def rpc(name, args):
    _runtime.mkdir(parents=True, exist_ok=True, mode=0o700)
    for attempt in range(30):
        try:
            reader, writer = await asyncio.open_unix_connection(str(_socket), limit=50_000_000)
            break
        except (ConnectionRefusedError, FileNotFoundError):
            if attempt == 0:
                log = open(_runtime / 'daemon.log', 'ab')
                subprocess.Popen([sys.executable, str(Path(__file__).resolve()), '--daemon'],
                                 stdin=subprocess.DEVNULL, stdout=log, stderr=log,
                                 start_new_session=True)
                log.close()
            await asyncio.sleep(0.1)
    else:
        raise RuntimeError('No se pudo iniciar el controlador local de Firefox.')
    try:
        writer.write((json.dumps({'tool': name, 'args': args})+'\n').encode())
        await writer.drain()
        response = json.loads(await asyncio.wait_for(reader.readline(), 125))
        if 'error' in response:
            raise RuntimeError(response['error'])
        return response['result']
    finally:
        writer.close()
        await writer.wait_closed()


def tool():
    def decorate(function):
        @functools.wraps(function)
        async def wrapped(*args, **kwargs):
            if _daemon_mode:
                return await function(*args, **kwargs)
            bound = inspect.signature(function).bind(*args, **kwargs)
            return await rpc(function.__name__, dict(bound.arguments))
        mcp.tool()(wrapped)
        return wrapped
    return decorate


_events = deque(maxlen=1000)
_READ_METHODS = {'browsingContext.getTree', 'session.status'}


async def disconnect():
    global _ws
    ws, _ws = _ws, None
    if ws is not None:
        try:
            await ws.close()
        except Exception:
            pass


async def _send(method, params):
    global _sequence
    _sequence += 1
    request_id = _sequence
    await _ws.send(json.dumps({'id': request_id, 'method': method, 'params': params}))
    async with asyncio.timeout(60):
        while True:
            message = json.loads(await _ws.recv())
            if message.get('type') == 'event':
                _events.append(message)
            elif message.get('id') == request_id:
                if message.get('type') == 'error':
                    raise RuntimeError(f"{message.get('error')}: {message.get('message')}")
                return message.get('result', {})


async def command(method, params):
    global _ws, _session_active
    async with _lock:
        for attempt in range(2):
            try:
                if _ws is None or _ws.state != State.OPEN:
                    await disconnect()
                    _ws = await connect('ws://127.0.0.1:9222/session', open_timeout=3, max_size=50_000_000)
                    try:
                        await _send('session.new', {'capabilities': {}})
                    except Exception:
                        await disconnect()
                        raise
                    _session_active = True
                return await _send(method, params)
            except ConnectionClosed:
                await disconnect()
                if attempt or method not in _READ_METHODS:
                    raise RuntimeError('Firefox cerró la conexión; no se repitió la acción.')
            except TimeoutError:
                # A late response retains its ID and is skipped by the next command.
                raise RuntimeError('Firefox no respondió en 60 s. Comprueba el resultado antes de repetir la acción.')
            except Exception:
                if _ws is not None and _ws.state != State.OPEN:
                    await disconnect()
                raise


def http_url(url):
    if urlsplit(url).scheme not in ('http', 'https') or not urlsplit(url).hostname:
        raise ValueError('Se requiere una URL HTTP o HTTPS absoluta.')
    return url


def value(result):
    if result.get('type') == 'exception':
        raise RuntimeError(result.get('exceptionDetails', {}).get('text', 'Error de JavaScript'))
    remote = result.get('result', {})
    if remote.get('type') == 'string':
        return json.loads(remote['value'])
    return remote.get('value')


@tool()
async def evaluar(context: str, expresion: str):
    """Evaluar JavaScript en una pestaña del usuario y devolver JSON; propaga excepciones."""
    return value(await command('script.evaluate', {
        'expression': '(async()=>JSON.stringify(await (' + expresion + ')))()',
        'target': {'context': context}, 'awaitPromise': True}))


@tool()
async def pestanas():
    """Listar pestañas y sus iframes con sus identificadores context."""
    return await command('browsingContext.getTree', {})


@tool()
async def abrir(url: str):
    """Abrir una URL HTTP/HTTPS en una pestaña nueva y devolver su context."""
    http_url(url)
    context = (await command('browsingContext.create', {'type': 'tab'}))['context']
    try:
        return {'context': context, **await navegar(context, url)}
    except Exception as exc:
        raise RuntimeError(f'No se confirmó la navegación; context={context}. {exc}') from exc


@tool()
async def navegar(context: str, url: str):
    """Navegar una pestaña; esperar DOM interactivo, sin bloquear por recursos secundarios."""
    return await command('browsingContext.navigate', {'context': context, 'url': http_url(url), 'wait': 'interactive'})


@tool()
async def leer(context: str):
    """Leer título, texto, enlaces y controles sin exponer valores de campos."""
    return await evaluar(context, """({title:document.title,url:location.href,
      text:document.body?.innerText?.slice(0,50000),
      links:[...document.querySelectorAll('a[href]')].slice(0,300).map(a=>({text:a.innerText.trim(),url:a.href})),
      controls:[...document.querySelectorAll('button,input,select,textarea,[role=button]')].slice(0,150)
        .map(e=>({tag:e.tagName,id:e.id,name:e.name,type:e.type,label:e.getAttribute('aria-label'),text:e.innerText?.slice(0,150)})),
      frames:[...document.querySelectorAll('iframe')].map(e=>({id:e.id,src:e.src,title:e.title}))})""")


async def element(context, selector):
    result = await command('script.evaluate', {
        'expression': '(()=>{const e=document.querySelector(' + json.dumps(selector) + ");if(!e)throw Error('Elemento no encontrado');e.scrollIntoView({block:'center',inline:'center'});return e})()",
        'target': {'context': context}, 'awaitPromise': True})
    if result.get('type') == 'exception':
        raise RuntimeError(result.get('exceptionDetails', {}).get('text', 'Elemento no encontrado'))
    node = result.get('result', {})
    if not node.get('sharedId'):
        raise RuntimeError('El selector no identifica un nodo DOM.')
    return {'type': 'element', 'element': {'sharedId': node['sharedId']}}


@tool()
async def hacer_clic(context: str, selector: str):
    """Clic nativo de puntero en un selector CSS, con eventos confiables."""
    origin = await element(context, selector)
    return await command('input.performActions', {'context': context, 'actions': [{
        'type': 'pointer', 'id': 'mouse', 'parameters': {'pointerType': 'mouse'},
        'actions': [{'type': 'pointerMove', 'x': 0, 'y': 0, 'origin': origin},
                    {'type': 'pointerDown', 'button': 0}, {'type': 'pointerUp', 'button': 0}]}]})


@tool()
async def escribir(context: str, selector: str, texto: str):
    """Reemplazar texto con teclado nativo; sirve para input, textarea y contenteditable."""
    await hacer_clic(context, selector)
    actions = [{'type': 'keyDown', 'value': '\ue009'}, {'type': 'keyDown', 'value': 'a'},
               {'type': 'keyUp', 'value': 'a'}, {'type': 'keyUp', 'value': '\ue009'},
               {'type': 'keyDown', 'value': '\ue003'}, {'type': 'keyUp', 'value': '\ue003'}]
    for char in texto:
        actions.extend([{'type': 'keyDown', 'value': char}, {'type': 'keyUp', 'value': char}])
    try:
        return await command('input.performActions', {'context': context, 'actions': [
            {'type': 'key', 'id': 'keyboard', 'actions': actions}]})
    finally:
        await command('input.releaseActions', {'context': context})


@tool()
async def tecla(context: str, teclas: list[str]):
    """Pulsar teclas de página, p. ej. ['Control','f'] o ['Escape']. Para pestañas usar accion_pestana."""
    mapping = {'Control': '\ue009', 'Shift': '\ue008', 'Alt': '\ue00a', 'Meta': '\ue03d',
               'Enter': '\ue007', 'Escape': '\ue00c', 'Tab': '\ue004', 'Backspace': '\ue003',
               'ArrowLeft': '\ue012', 'ArrowRight': '\ue014', 'ArrowUp': '\ue013', 'ArrowDown': '\ue015'}
    keys = [mapping.get(k, k) for k in teclas]
    if not keys or any(len(k) != 1 for k in keys):
        raise ValueError('Usa caracteres individuales o nombres de teclas admitidos.')
    try:
        return await command('input.performActions', {'context': context, 'actions': [{
            'type': 'key', 'id': 'keyboard', 'actions':
            [{'type': 'keyDown', 'value': k} for k in keys] +
            [{'type': 'keyUp', 'value': k} for k in reversed(keys)]}]})
    finally:
        await command('input.releaseActions', {'context': context})


@tool()
async def accion_pestana(context: str, accion: str):
    """activar, cerrar, recargar, atras o adelante sin depender de atajos de la interfaz."""
    methods = {'activar': ('browsingContext.activate', {}), 'cerrar': ('browsingContext.close', {}),
               'recargar': ('browsingContext.reload', {'wait': 'interactive'}),
               'atras': ('browsingContext.traverseHistory', {'delta': -1}),
               'adelante': ('browsingContext.traverseHistory', {'delta': 1})}
    if accion not in methods:
        raise ValueError('Acción admitida: ' + ', '.join(methods))
    method, params = methods[accion]
    return await command(method, {'context': context, **params})


@tool()
async def captura(context: str, destino: str):
    """Guardar una captura PNG de la pestaña en una ruta absoluta local."""
    path = Path(destino).expanduser()
    if not path.is_absolute() or path.suffix.lower() != '.png':
        raise ValueError('Usa una ruta absoluta con extensión .png.')
    if path.exists():
        raise ValueError('La captura ya existe; elige otro nombre.')
    result = await command('browsingContext.captureScreenshot', {'context': context})
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(base64.b64decode(result['data']))
    return {'path': str(path), 'bytes': path.stat().st_size}


@tool()
async def atajos(context: str):
    """Listar accesos HTTP/HTTPS de la pestaña de inicio, sin sus consultas privadas."""
    return await evaluar(context, """[...document.querySelectorAll('a[href]')].filter(a=>/^https?:$/.test(new URL(a.href).protocol))
      .map(a=>{const u=new URL(a.href);return {nombre:a.innerText.trim()||a.title||a.getAttribute('aria-label'),url:u.origin+u.pathname}})""")


@tool()
async def abrir_atajo(context: str, nombre: str):
    """Abrir un acceso de la pestaña de inicio por nombre exacto, conservando su URL interna."""
    url = await evaluar(context, '(()=>{const links=[...document.querySelectorAll("a[href]")];const e=links.find(a=>(a.innerText.trim()||a.title||a.getAttribute("aria-label")||"").toLowerCase()===' + json.dumps(nombre.lower()) + ');if(!e)throw Error("Atajo no encontrado");return e.href})()')
    return await abrir(url)


@tool()
async def descargar(context: str, url: str, carpeta: str):
    """Descargar un enlace con la sesión Firefox, esperar downloadEnd y comprobar su archivo."""
    http_url(url)
    folder = Path(carpeta).expanduser()
    if not folder.is_absolute():
        raise ValueError('Usa una carpeta absoluta.')
    folder.mkdir(parents=True, exist_ok=True)
    tree = await command('browsingContext.getTree', {'root': context})
    user_context = tree['contexts'][0]['userContext']
    before = {p for p in folder.iterdir() if p.is_file()}
    await command('session.subscribe', {'events': ['browsingContext.downloadWillBegin', 'browsingContext.downloadEnd'], 'contexts': [context]})
    await command('browser.setDownloadBehavior', {'downloadBehavior': {'type': 'allowed', 'destinationFolder': str(folder)}, 'userContexts': [user_context]})
    _events.clear()
    try:
        try:
            await command('browsingContext.navigate', {'context': context, 'url': url, 'wait': 'none'})
        except RuntimeError as exc:
            if 'download' not in str(exc).lower():
                raise
        deadline = asyncio.get_running_loop().time() + 45
        while asyncio.get_running_loop().time() < deadline:
            await command('browsingContext.getTree', {'root': context})
            ends = [e['params'] for e in _events if e['method'] == 'browsingContext.downloadEnd' and e['params'].get('context') == context]
            for end in ends:
                if end.get('status') == 'canceled':
                    raise RuntimeError('Firefox canceló la descarga.')
                if end.get('status') == 'complete':
                    path = Path(end.get('filepath', ''))
                    if path.is_file() and path.stat().st_size > 0:
                        return {'path': str(path), 'bytes': path.stat().st_size, 'status': 'complete'}
            # shortcut: older Firefox may omit filepath; report only new completed files.
            files = [p for p in folder.iterdir() if p not in before and p.is_file() and p.suffix != '.part' and p.stat().st_size > 0 and not Path(str(p)+'.part').exists()]
            if files and ends:
                return {'files': [str(p) for p in files], 'status': 'complete'}
            await asyncio.sleep(0.25)
        raise RuntimeError('No se confirmó una descarga en 45 s; inspecciona la pestaña y la carpeta antes de reintentar.')
    finally:
        await command('browser.setDownloadBehavior', {'downloadBehavior': None, 'userContexts': [user_context]})
        await command('session.unsubscribe', {'events': ['browsingContext.downloadWillBegin', 'browsingContext.downloadEnd'], 'contexts': [context]})


async def serve():
    _runtime.mkdir(parents=True, exist_ok=True, mode=0o700)
    lock = open(_runtime / 'daemon.lock', 'w')
    try:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except BlockingIOError:
        return
    _socket.unlink(missing_ok=True)
    async def handle(reader, writer):
        try:
            request = json.loads(await reader.readline())
            name = request['tool']
            function = globals().get(name)
            if name not in {'pestanas','abrir','navegar','leer','evaluar','hacer_clic','escribir','tecla',
                            'accion_pestana','captura','atajos','abrir_atajo','descargar'}:
                raise ValueError('Herramienta desconocida.')
            async with _rpc_lock:
                result = await function(**request.get('args', {}))
            response = {'result': result}
        except Exception as exc:
            response = {'error': str(exc)}
        try:
            writer.write((json.dumps(response, ensure_ascii=False)+'\n').encode())
            await writer.drain()
        finally:
            writer.close()
            await writer.wait_closed()
    server = await asyncio.start_unix_server(handle, path=str(_socket), limit=50_000_000)
    _socket.chmod(0o600)
    stopped = asyncio.Event()
    for sig in (signal.SIGTERM, signal.SIGINT):
        asyncio.get_running_loop().add_signal_handler(sig, stopped.set)
    try:
        async with server:
            await stopped.wait()
    finally:
        if _ws is not None and _session_active:
            try:
                await _send('session.end', {})
            except Exception:
                pass
        await disconnect()
        _socket.unlink(missing_ok=True)
        lock.close()


async def cli(name, params):
    functions = {'pestanas': pestanas, 'abrir': abrir, 'navegar': navegar, 'leer': leer,
                 'evaluar': evaluar, 'hacer_clic': hacer_clic, 'escribir': escribir, 'tecla': tecla,
                 'accion_pestana': accion_pestana, 'captura': captura, 'atajos': atajos,
                 'abrir_atajo': abrir_atajo, 'descargar': descargar}
    try:
        if name not in functions:
            raise ValueError('Herramienta desconocida: ' + name)
        print(json.dumps(await functions[name](**params), ensure_ascii=False))
    finally:
        # The local controller owns the session; CLI disconnects do not end it.
        await disconnect()


if __name__ == '__main__':
    if _daemon_mode:
        asyncio.run(serve())
    elif len(sys.argv) == 3 and sys.argv[1] == '--call':
        call = json.loads(sys.argv[2])
        try:
            asyncio.run(cli(call['tool'], call.get('args', {})))
        except Exception as exc:
            print(json.dumps({'error': str(exc)}, ensure_ascii=False))
            raise SystemExit(1)
    else:
        mcp.run()
