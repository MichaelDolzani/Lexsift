import json
import socket
import threading
import time
from http.server import BaseHTTPRequestHandler, HTTPServer

import pytest

from lexsift import tools


class Handler(BaseHTTPRequestHandler):
    delay = 0.0

    def do_POST(self):
        body = json.loads(self.rfile.read(int(self.headers["Content-Length"])))
        time.sleep(self.delay)
        payload = json.dumps({"result": body["action"], "error": None}).encode()
        self.send_response(200)
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)

    def log_message(self, *args):
        pass


@pytest.fixture
def anki_server():
    server = HTTPServer(("127.0.0.1", 0), Handler)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    yield f"http://127.0.0.1:{server.server_port}"
    server.shutdown()


def test_invoke_returns_result(anki_server):
    Handler.delay = 0.0
    assert tools.invoke("version", anki_server) == "version"


def test_invoke_times_out_instead_of_hanging(anki_server, monkeypatch):
    Handler.delay = 1.0
    monkeypatch.setattr(tools, "ANKI_TIMEOUT", 0.2)
    start = time.time()
    with pytest.raises((socket.timeout, TimeoutError, OSError)):
        tools.invoke("version", anki_server)
    assert time.time() - start < 0.9


def test_field_query_plain():
    assert tools.anki_field_query("Word", "Hund") == '"Word:Hund"'


def test_field_query_escapes_quotes_wildcards_and_backslashes():
    assert tools.anki_field_query("Word", 'say "hi"') == r'"Word:say \"hi\""'
    assert tools.anki_field_query("Word", "a*b_c") == r'"Word:a\*b\_c"'
    assert tools.anki_field_query("Word", "back\\slash") == r'"Word:back\\slash"'
    assert tools.anki_field_query("Word", "12:30") == '"Word:12:30"'
