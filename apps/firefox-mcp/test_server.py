import asyncio
import json
import unittest
from unittest.mock import AsyncMock, patch
from websockets.protocol import State
import server as f

class FakeWebSocket:
    def __init__(self, state=State.OPEN):
        self.state = state
        self.messages = []
        self.sent = []
    async def send(self, text):
        request = json.loads(text)
        self.sent.append(request['method'])
        self.messages.extend([
            {'type':'event','method':'browsingContext.downloadEnd','params':{'status':'complete'}},
            {'type':'success','id':request['id']-1,'result':{'old':True}},
            {'type':'success','id':request['id'],'result':{'contexts':[]}}])
    async def recv(self):
        return json.dumps(self.messages.pop(0))
    async def close(self):
        raise RuntimeError('close failed')

class ConnectionTests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.old_ws = f._ws
    async def asyncTearDown(self):
        f._ws = self.old_ws
    async def test_failed_close_still_discards_socket(self):
        f._ws = FakeWebSocket(State.CLOSED)
        await f.disconnect()
        self.assertIsNone(f._ws)
    async def test_first_read_after_closed_socket_reconnects(self):
        f._ws = FakeWebSocket(State.CLOSED)
        fresh = FakeWebSocket()
        with patch.object(f, 'connect', AsyncMock(return_value=fresh)):
            self.assertEqual(await f.command('browsingContext.getTree',{}),{'contexts':[]})
        self.assertEqual(fresh.sent,['session.new','browsingContext.getTree'])
    async def test_events_and_late_responses_do_not_replace_result(self):
        f._ws=FakeWebSocket()
        self.assertEqual(await f._send('session.status',{}), {'contexts':[]})
    def test_script_exception_is_an_error(self):
        with self.assertRaisesRegex(RuntimeError,'Elemento no encontrado'):
            f.value({'type':'exception','exceptionDetails':{'text':'Elemento no encontrado'}})
    def test_invalid_urls_are_rejected(self):
        for url in ('file:///etc/passwd','javascript:alert(1)','https:missing-host'):
            with self.assertRaises(ValueError):f.http_url(url)

if __name__ == '__main__':
    unittest.main()
