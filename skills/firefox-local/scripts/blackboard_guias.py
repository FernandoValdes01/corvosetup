"""Descargar guías publicadas del periodo solicitado usando la sesión del Firefox personal."""
import argparse
import asyncio
import hashlib
from html.parser import HTMLParser
import json
import re
import sys
import unicodedata
import zipfile
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path.home()/'.local/share/corvosetup/mcp/firefox-local'))
import server as firefox


def normal(text):
    return ''.join(c for c in unicodedata.normalize('NFKD', text.lower()) if not unicodedata.combining(c))


def is_guide(node):
    filename = node.get('file', {}).get('fileName', '')
    text = normal(node.get('title', '') + ' ' + filename)
    return ('guia' in text and 'aprendiz' in text) or bool(re.match(r'^ga\s+info\s*\d+', normal(filename)))


class GuideLinks(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links = []
        self.anchor = None

    def handle_starttag(self, tag, attrs):
        if tag != 'a':
            return
        attrs = dict(attrs)
        metadata = json.loads(attrs.get('data-bbfile', '{}'))
        self.anchor = {'title': '', 'file': {'fileName': metadata.get('fileName', '')}, 'href': attrs.get('href', '')}

    def handle_data(self, data):
        if self.anchor is not None:
            self.anchor['title'] += data

    def handle_endtag(self, tag):
        if tag == 'a' and self.anchor is not None:
            if self.anchor['href'] and is_guide(self.anchor):
                self.links.append(self.anchor)
            self.anchor = None


def inline_guides(body):
    parser = GuideLinks()
    parser.feed(body)
    return parser.links


def verify(path):
    if not path.is_file() or not path.stat().st_size:
        raise ValueError(f'Archivo vacío o ausente: {path.name}')
    extra = {}
    if path.suffix.lower() == '.pdf':
        if not path.read_bytes().startswith(b'%PDF-'):
            raise ValueError(f'No es un PDF: {path.name}')
    elif path.suffix.lower() == '.docx':
        with zipfile.ZipFile(path) as archive:
            if archive.testzip() or 'word/document.xml' not in archive.namelist():
                raise ValueError(f'DOCX inválido: {path.name}')
            import xml.etree.ElementTree as ET
            root = ET.fromstring(archive.read('word/document.xml'))
            text = ' '.join(e.text for e in root.iter() if e.tag.endswith('}t') and e.text)
            if 'Nombre del Curso Código' in text:
                extra['observacion'] = 'Plantilla institucional sin completar, publicada en el curso.'
    else:
        raise ValueError(f'Formato de guía sin validación: {path.suffix}')
    return {'bytes': path.stat().st_size, 'sha256': hashlib.sha256(path.read_bytes()).hexdigest(), **extra}


async def api(context, path):
    expression = '''(async()=>{const r=await fetch(location.origin+PATH,{headers:{Accept:'application/json'}});
      if(!r.ok)throw Error('Blackboard HTTP '+r.status);return await r.json()})()'''.replace('PATH', json.dumps(path))
    return await firefox.evaluar(context, expression)


async def pages(context, path):
    results = []
    visited = set()
    while path:
        if not path.startswith('/learn/api/') or path in visited:
            raise ValueError('Paginación de Blackboard inesperada.')
        visited.add(path)
        data = await api(context, path)
        results.extend(data.get('results', []))
        path = data.get('paging', {}).get('nextPage')
    return results


async def crawl(context, course):
    root = '/learn/api/public/v1/courses/' + course['id'] + '/contents'
    queue = [root+'?limit=100']
    seen = set()
    nodes = []
    while queue:
        path = queue.pop(0)
        if path in seen:
            continue
        if len(seen) >= 300:
            raise ValueError('Límite de seguridad de carpetas alcanzado.')
        seen.add(path)
        children = await pages(context, path)
        for node in children:
            nodes.append({'id': node['id'], 'title': node.get('title', ''),
                          'file': node.get('contentHandler', {}).get('file', {}),
                          'handler': node.get('contentHandler', {}).get('id'),
                          'body': node.get('body', '')})
            if node.get('hasChildren'):
                queue.append(root+'/'+node['id']+'/children?limit=100')
    return nodes


async def main(args):
    folder = Path(args.destino).expanduser().resolve()
    folder.mkdir(parents=True, exist_ok=True)
    contexts = (await firefox.pestanas())['contexts']
    context = args.context or next((t['context'] for t in contexts if t['url'].startswith('https://educa.blackboard.com/ultra')), None)
    if context is None:
        raise RuntimeError('Inicia sesión en Educa Blackboard antes de descargar las guías.')
    memberships = await pages(context, '/learn/api/public/v1/users/me/courses?expand=course&limit=100')
    courses = [m for m in memberships if m.get('course', {}).get('courseId', '').endswith('-'+args.periodo)]
    manifest = {'periodo': args.periodo, 'consultado': datetime.now(timezone.utc).isoformat(), 'cursos': []}
    work = None
    try:
        for membership in courses:
            course = membership['course']
            code = course['courseId']
            if not re.fullmatch(r'[\w.-]+', code):
                raise ValueError('Código de curso inesperado.')
            record = {'codigo': code, 'nombre': course['name'], 'url': course.get('externalAccessUrl'),
                      'rol': membership.get('courseRoleId'), 'archivos': []}
            manifest['cursos'].append(record)
            if membership.get('availability', {}).get('available') != 'Yes':
                record['estado'] = 'Inscripción deshabilitada'
                continue
            try:
                nodes = await crawl(context, course)
                record['contenidos_revisados'] = len(nodes)
                candidates = [n for n in nodes if is_guide(n) and n.get('file')]
                record['estado'] = 'Descargado' if candidates else 'Sin guía de aprendizaje publicada'
                # Report potential inline guides rather than silently treating them as absent.
                inline = [n['id'] for n in nodes if inline_guides(n.get('body', ''))]
                if inline:
                    record['documentos_para_revisar'] = inline
                for node in candidates:
                    base = '/learn/api/public/v1/courses/'+course['id']+'/contents/'+node['id']
                    attachments = await pages(context, base+'/attachments?limit=100')
                    if not attachments:
                        raise ValueError('Guía sin adjuntos: '+node['title'])
                    for attachment in attachments:
                        course_folder = folder/code
                        filename = Path(attachment['fileName']).name
                        target = course_folder/filename
                        if not target.exists():
                            if work is None:
                                work = (await firefox.abrir('https://educa.blackboard.com/ultra/course'))['context']
                            result = await firefox.descargar(work, 'https://educa.blackboard.com'+base+'/attachments/'+attachment['id']+'/download', str(course_folder))
                            target = Path(result.get('path') or result['files'][0])
                        checks = verify(target)
                        record['archivos'].append({'nombre_original': attachment['fileName'],
                            'titulo_publicado': node['title'], 'contenido_id': node['id'],
                            'ruta': str(target.relative_to(folder)), **checks})
                        print(code, target.name, checks['bytes'], 'bytes', flush=True)
                if record['archivos'] and all(a.get('observacion') for a in record['archivos']):
                    record['estado'] = 'Solo plantilla institucional sin completar'
            except Exception as exc:
                record['estado'] = 'Pendiente: '+str(exc)
                print(code, record['estado'], flush=True)
            (folder/'manifest.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2))
    finally:
        if work is not None:
            await firefox.accion_pestana(work, 'cerrar')
    rows = ['# Guías de aprendizaje, '+args.periodo, '', 'Archivos descargados desde la sesión personal de Educa Blackboard. Los nombres originales se conservan.', '']
    for course in manifest['cursos']:
        rows += ['## '+course['nombre']+' · '+course['codigo'], '', course['estado'], '']
        for file in course['archivos']:
            rows.append('- ['+file['nombre_original']+'](<' + file['ruta'] + '>) · '+str(file['bytes'])+' bytes'+(' · '+file['observacion'] if file.get('observacion') else ''))
        rows.append('')
    (folder/'INDICE.md').write_text('\n'.join(rows))
    failures = [c for c in manifest['cursos'] if c['estado'].startswith('Pendiente') or c.get('documentos_para_revisar')]
    print(json.dumps({'files': sum(len(c['archivos']) for c in manifest['cursos']), 'courses': len(courses), 'needs_review': len(failures)}, ensure_ascii=False))
    if failures:
        raise SystemExit(2)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--context')
    parser.add_argument('--periodo', required=True)
    parser.add_argument('--destino', required=True)
    args = parser.parse_args()
    if not re.fullmatch(r'20\d{2}-[12]', args.periodo):
        parser.error('Periodo esperado: año-semestre, por ejemplo 2026-2')
    asyncio.run(main(args))
