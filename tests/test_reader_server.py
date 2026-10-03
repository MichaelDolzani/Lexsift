import zipfile

import pytest

from lexsift.global_names import settings
from lexsift.reader import server


def make_epub(path):
    with zipfile.ZipFile(path, "w") as z:
        z.writestr("mimetype", "application/epub+zip")


@pytest.fixture
def client(tmp_path, monkeypatch):
    books = tmp_path / "books"
    books.mkdir()
    make_epub(books / "inside.epub")
    make_epub(tmp_path / "outside.epub")
    old = settings.value("books_dir")
    settings.setValue("books_dir", str(books))
    parsed = []
    monkeypatch.setattr(server, "getEpubMetadata", lambda p: parsed.append(p) or {"title": "t", "author": "a"})
    if "read_epub" not in server.app.view_functions:  # the module-level app takes routes only once
        monkeypatch.setattr(server, "serve", lambda *a, **k: None)  # register routes without blocking
        server.ReaderServer(None, "127.0.0.1", 0).start_api()
    yield server.app.test_client(), parsed, tmp_path
    settings.setValue("books_dir", old if old is not None else "")


def test_reads_book_inside_books_folder(client):
    c, parsed, _ = client
    assert c.get("/read/inside.epub").status_code == 200
    assert parsed[-1].endswith("inside.epub")


def test_refuses_paths_outside_books_folder(client):
    c, parsed, _ = client
    # %2F keeps the client from normalising the path; the route then receives "../outside.epub"
    assert c.get("/read/..%2Foutside.epub").status_code == 404
    assert parsed == []
