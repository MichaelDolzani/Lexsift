import os
from types import SimpleNamespace

import pytest

from lexsift.importer.KindleVocabImporter import KindleVocabImporter
from lexsift.importer.utils import koreader_metadata_path, koreader_scandir
from lexsift.models import DisplayMode, LemmaPolicy, SourceOptions
from lexsift.sources import google_translate_source, wiktionary_source

OPTIONS = SourceOptions(LemmaPolicy.no_lemma, DisplayMode.html, 0, 0)


class FakeResponse:
    def __init__(self, data, status_code=200):
        self._data = data
        self.status_code = status_code
        self.text = str(data)

    def json(self):
        if isinstance(self._data, Exception):
            raise self._data
        return self._data


def test_google_translate_hebrew_uses_iw_but_keeps_he_for_lemmas(monkeypatch):
    urls = []
    monkeypatch.setattr(google_translate_source, "cached_get",
                        lambda url: urls.append(url) or FakeResponse({"translation": "dog"}))
    source = google_translate_source.GoogleTranslateSource("he", OPTIONS, "https://lingva.example", "en")
    assert source._lookup("כלב").definition == "dog"
    assert "/api/v1/iw/en/" in urls[0]
    assert source.langcode == "he"


def test_google_translate_error_page_is_an_error_not_a_crash(monkeypatch):
    monkeypatch.setattr(google_translate_source, "cached_get", lambda url: FakeResponse({"error": "nope"}))
    source = google_translate_source.GoogleTranslateSource("de", OPTIONS, "https://lingva.example", "en")
    assert source._lookup("Hund").error


def test_wiktionary_encodes_word_and_escapes_definitions(monkeypatch):
    urls = []
    data = {"en": [{"partOfSpeech": "Noun",
                    "definitions": [{"definition": "<span>a &lt;tag&gt; &amp; more</span>"}]}]}
    monkeypatch.setattr(wiktionary_source, "cached_get", lambda url: urls.append(url) or FakeResponse(data))
    source = wiktionary_source.WiktionarySource("en", OPTIONS)
    result = source._lookup("AC/DC?")
    assert urls[0].endswith("/page/definition/AC%2FDC%3F")
    assert result.definition == "<i>Noun</i><br>1. a &lt;tag&gt; &amp; more"


@pytest.mark.parametrize("book, expected", [
    ("lib/book.epub", "lib/book.sdr/metadata.epub.lua"),
    ("lib/book.fb2.zip", "lib/book.fb2.sdr/metadata.zip.lua"),
    ("lib/book.fb2", "lib/book.sdr/metadata.fb2.lua"),
])
def test_koreader_metadata_path(book, expected):
    assert koreader_metadata_path(book) == expected


def test_koreader_scandir_finds_fb2_zip_books(tmp_path):
    for book in ["a.epub", "b.fb2.zip"]:
        (tmp_path / book).write_text("")
        meta = koreader_metadata_path(str(tmp_path / book))
        os.makedirs(os.path.dirname(meta))
        open(meta, "w").close()
    found = sorted(os.path.basename(f) for f in koreader_scandir(str(tmp_path)))
    assert found == ["a.epub", "b.fb2.zip"]


def test_kindle_wrong_path_does_not_create_database(tmp_path):
    with pytest.raises(FileNotFoundError):
        KindleVocabImporter.getNotes(SimpleNamespace(path=str(tmp_path)))
    assert not (tmp_path / "system").exists()
