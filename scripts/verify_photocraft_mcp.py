# /// script
# requires-python = ">=3.11"
# dependencies = ["mcp==1.30.0"]
# ///
"""Real PhotoCraft MCP roundtrip using synthetic images, never user photographs."""
import asyncio
import base64
import hashlib
import json
import os
from pathlib import Path
import struct
import tempfile
import zlib

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


def png_fixture(path):
    def chunk(kind, data):
        return struct.pack('>I', len(data)) + kind + data + struct.pack('>I', zlib.crc32(kind+data))
    width, height = 64, 48
    # A colored diamond on alpha exercises embedded image compositing.
    rows = b''.join(b'\0' + b''.join(bytes((220, 70, 30, 255 if abs(x-32)+abs(y-24) < 22 else 0))
                                  for x in range(width)) for y in range(height))
    path.write_bytes(b'\x89PNG\r\n\x1a\n' + chunk(b'IHDR', struct.pack('>IIBBBBB', width, height, 8, 6, 0, 0, 0))
                     + chunk(b'IDAT', zlib.compress(rows)) + chunk(b'IEND', b''))


def png_size(data):
    assert data.startswith(b'\x89PNG\r\n\x1a\n')
    return struct.unpack('>II', data[16:24])


async def main():
    home = Path.home()
    root = home / 'Imágenes/PhotoCraft/pruebas'
    root.mkdir(parents=True, exist_ok=True)
    out = Path(tempfile.mkdtemp(prefix='mcp-', dir=root))
    source = out / 'recurso.png'
    png_fixture(source)
    digest = hashlib.sha256(source.read_bytes()).hexdigest()
    wrapper = home / '.local/bin/corvosetup-mcp-photocraft'
    calls = []
    env = {**os.environ, 'PHOTOCRAFT_READ_ROOT': str(out), 'PHOTOCRAFT_WRITE_ROOT': str(out)}
    async with stdio_client(StdioServerParameters(command=str(wrapper), env=env)) as (reader, writer):
        async with ClientSession(reader, writer) as session:
            init = await session.initialize()
            assert init.serverInfo.name == 'photocraft'
            tools = await session.list_tools()
            names = {t.name for t in tools.tools}
            assert {'command_run', 'doc_place', 'doc_save', 'doc_export', 'render_preview'} <= names

            async def call(tool_name, **arguments):
                result = await session.call_tool(tool_name, arguments)
                assert not result.isError, result
                payload = json.loads('\n'.join(c.text for c in result.content if c.type == 'text'))
                calls.append({'tool': tool_name, 'arguments': arguments, 'result': payload})
                return payload

            async def preview():
                result = await session.call_tool('render_preview', {'max_side': 320})
                assert not result.isError, result
                content = next(c for c in result.content if c.type == 'image')
                data = base64.b64decode(content.data)
                assert png_size(data) == (320, 240)
                return data

            await call('doc_new', width=320, height=240, background='#e9eef5', name='Prueba PhotoCraft MCP')
            before = await preview()
            await call('doc_place', path=str(source), center=[160, 120], scale=200)
            placed = await call('doc_inspect')
            assert len(placed['layers']) == 2
            layer = next(l for l in placed['layers'] if l['kind'] == 'Smart Object')
            assert layer['smartSource']['kind'] == 'embedded'
            bounds = layer['bounds']
            await call('command_run', id='edit.transform', params={'scaleX': 80, 'scaleY': 80, 'rotate': 15, 'dx': 20, 'dy': 5})
            transformed = await call('doc_inspect')
            changed = next(l for l in transformed['layers'] if l['id'] == layer['id'])['bounds']
            assert bounds != changed
            await call('command_run', id='edit.undo', params={})
            restored = await call('doc_inspect')
            assert next(l for l in restored['layers'] if l['id'] == layer['id'])['bounds'] == bounds
            await call('command_run', id='edit.transform', params={'scaleX': 80, 'scaleY': 80, 'rotate': 15, 'dx': 20, 'dy': 5})
            after = await preview()
            assert before != after
            (out / 'preview.png').write_bytes(after)
            await call('doc_save', path=str(out / 'composicion.pcraft'))
            await call('doc_export', path=str(out / 'composicion.png'), format='png')
            assert png_size((out / 'composicion.png').read_bytes()) == (320, 240)
            await call('doc_close')
            await call('doc_open', path=str(out / 'composicion.pcraft'))
            reopened = await call('doc_inspect')
            assert len(reopened['layers']) == 2
            embedded = next(l for l in reopened['layers'] if l['kind'] == 'Smart Object')
            assert embedded['bounds'] == changed
            assert embedded['smartSource']['kind'] == 'embedded'
            assert await preview() == after
            # Roots must actually prevent access, rather than merely appear in config.
            denied = await session.call_tool('doc_export', {'path': str(out.parent / 'outside.png'), 'format': 'png'})
            assert denied.isError and not (out.parent / 'outside.png').exists()
            assert hashlib.sha256(source.read_bytes()).hexdigest() == digest
            catalog = await call('command_list')
            command_count = len(catalog)
    report = {'status': 'passed', 'server': init.serverInfo.model_dump(), 'tools': sorted(names),
              'commands': command_count, 'source_sha256': digest,
              'checks': ['MCP initialize/tools', 'document creation', 'embedded layer import',
                         'transform', 'undo', 'image preview changed', 'PNG export size',
                         'save/reopen with layers and identical preview', 'write-root enforced',
                         'original unchanged'], 'calls': calls}
    (out / 'report.json').write_text(json.dumps(report, ensure_ascii=False, indent=2))
    print(json.dumps({'status': 'passed', 'artifacts': str(out), 'commands': command_count}, ensure_ascii=False))


if __name__ == '__main__':
    asyncio.run(main())
