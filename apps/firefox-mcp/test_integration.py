"""Prueba real del perfil Firefox, con una página y descarga locales temporales."""
import asyncio
import json
import tempfile
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import server as f

PAYLOAD = b'%PDF-1.4\nFirefox local download fixture\n%%EOF\n'
class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/fixture.pdf':
            data = PAYLOAD
            self.send_response(200)
            self.send_header('Content-Type', 'application/pdf')
            self.send_header('Content-Disposition', 'attachment; filename="fixture.pdf"')
        else:
            data = b'''<!doctype html><title>Firefox local fixture</title>
            <input id="text"><div id="edit" contenteditable>old</div>
            <button id="click" onclick="window.trusted=event.isTrusted">Click</button>
            <a href="/fixture.pdf">Fixture</a>'''
            self.send_response(200)
            self.send_header('Content-Type', 'text/html; charset=utf-8')
        self.send_header('Content-Length', str(len(data)))
        self.end_headers()
        self.wfile.write(data)
    def log_message(self, *args):
        pass

async def main():
    with tempfile.TemporaryDirectory(prefix='firefox-local-test-') as folder:
        http = ThreadingHTTPServer(('127.0.0.1', 0), Handler)
        threading.Thread(target=http.serve_forever, daemon=True).start()
        origin = 'http://127.0.0.1:' + str(http.server_port)
        context = (await f.abrir(origin))['context']
        try:
            await f.hacer_clic(context, '#click')
            assert await f.evaluar(context, 'window.trusted') is True
            try:
                await f.hacer_clic(context, '#missing')
            except RuntimeError as exc:
                assert 'Elemento no encontrado' in str(exc)
            else:
                raise AssertionError('Missing selector must fail')
            await f.escribir(context, '#text', 'Guía 2026')
            assert await f.evaluar(context, 'document.querySelector("#text").value') == 'Guía 2026'
            await f.escribir(context, '#edit', 'editable')
            assert await f.evaluar(context, 'document.querySelector("#edit").textContent') == 'editable'
            await f.accion_pestana(context, 'recargar')
            assert (await f.leer(context))['title'] == 'Firefox local fixture'
            shot = await f.captura(context, str(Path(folder)/'fixture.png'))
            assert Path(shot['path']).read_bytes().startswith(b'\x89PNG')
            result = await f.descargar(context, origin+'/fixture.pdf', folder)
            target = Path(folder)/'fixture.pdf'
            assert target.read_bytes() == PAYLOAD, result
            print(json.dumps({'status': 'PASS', 'checks': ['trusted-click','missing-selector-error','native-text','contenteditable','reload','screenshot','verified-download']}))
        finally:
            await f.accion_pestana(context, 'cerrar')
            http.shutdown()

if __name__ == '__main__':
    asyncio.run(main())
