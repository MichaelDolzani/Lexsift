import json
import os
import sqlite3

import pytest
from PyQt5.QtCore import QSettings

from lexsift.local_dictionary import LocalDictionary
from lexsift.models import SRSNote
from lexsift.record import Record
from lexsift.vocabsieve_import import VocabSieveProfile, import_profile, vocabsieve_datapath


def ini_settings(path):
    return QSettings(str(path), QSettings.IniFormat)


@pytest.fixture
def vocabsieve(tmp_path):
    "A VocabSieve profile: settings, records with a note, an imported dictionary, cached audio and images"
    datapath = tmp_path / "FreeLanguageTools" / "VocabSieve"
    datapath.mkdir(parents=True)
    settings = ini_settings(tmp_path / "vocabsieve.ini")
    settings.setValue("target_language", "de")
    settings.setValue("note_type", "vocabsieve-notes")
    settings.setValue("tags", "vocabsieve")
    settings.setValue("internal/configured", True)
    settings.setValue("custom_dicts", json.dumps([{"name": "my-dict", "type": "json", "path": "/x.json", "lang": "de"}]))
    settings.sync()

    rec = Record(settings, str(datapath))
    rec.recordNote(SRSNote(word="Hund", sentence="Der Hund schläft.",
                           image=str(datapath / "images" / "hund.jpg"),
                           audio_path=str(datapath / "forvo" / "de" / "Hund.mp3")), "{}")
    rec.recordNote(SRSNote(word="Katze", image="/elsewhere/katze.jpg"), "{}")
    rec.conn.close()

    LocalDictionary(str(datapath)).importdict({"hund": "dog"}, "de", "my-dict")
    (datapath / "images").mkdir()
    (datapath / "images" / "hund.jpg").write_bytes(b"jpg")
    (datapath / "forvo" / "de").mkdir(parents=True)
    (datapath / "forvo" / "de" / "Hund.mp3").write_bytes(b"mp3")
    (datapath / "log").mkdir()
    (datapath / "log" / "session.txt").write_text("old log")
    return VocabSieveProfile(settings, str(datapath))


@pytest.fixture
def lexsift(tmp_path):
    "A fresh Lexsift profile, with dict.db held open like the running app does"
    datapath = tmp_path / "Lexsift" / "Lexsift"
    datapath.mkdir(parents=True)
    settings = ini_settings(tmp_path / "lexsift.ini")
    settings.setValue("check_updates", False)
    settings.setValue("target_language", "en")
    settings.sync()
    Record(settings, str(datapath)).conn.close()
    open_dictdb = LocalDictionary(str(datapath))
    yield settings, str(datapath), open_dictdb
    open_dictdb.conn.close()


def test_vocabsieve_datapath_is_a_sibling_of_lexsift():
    lexsift = os.path.join("home", "u", ".local", "share", "Lexsift", "Lexsift")
    assert vocabsieve_datapath(lexsift) == os.path.join("home", "u", ".local", "share", "FreeLanguageTools", "VocabSieve")


def test_describe(vocabsieve):
    assert vocabsieve.describe() == "6 settings, records.db, dict.db, forvo, images"


def test_import_copies_settings_records_dictionaries_and_media(vocabsieve, lexsift):
    settings, datapath, open_dictdb = lexsift
    report = import_profile(vocabsieve, settings, datapath)

    assert report.settings_copied == 6
    assert report.copied == ["records.db", "dict.db", "forvo", "images"]
    # Settings are replaced, keeping the user's existing note type and tags
    assert settings.value("target_language") == "de"
    assert settings.value("note_type") == "vocabsieve-notes"
    assert settings.value("tags") == "vocabsieve"
    assert settings.value("check_updates") is None
    # The connection Lexsift already had open sees the imported dictionary
    assert open_dictdb.define("hund", "de", "my-dict") == "dog"
    # Media is copied, logs are not
    assert open(os.path.join(datapath, "images", "hund.jpg"), "rb").read() == b"jpg"
    assert os.path.exists(os.path.join(datapath, "forvo", "de", "Hund.mp3"))
    assert not os.path.exists(os.path.join(datapath, "log", "session.txt"))


def test_import_points_note_paths_at_the_copies(vocabsieve, lexsift):
    settings, datapath, _ = lexsift
    import_profile(vocabsieve, settings, datapath)
    with sqlite3.connect(os.path.join(datapath, "records.db")) as conn:
        rows = conn.execute("SELECT word, image, pronunciation FROM notes ORDER BY word").fetchall()
    assert rows == [
        ("Hund", os.path.join(datapath, "images", "hund.jpg"), os.path.join(datapath, "forvo", "de", "Hund.mp3")),
        ("Katze", "/elsewhere/katze.jpg", ""),  # paths outside the old profile are left alone
    ]


def test_import_backs_up_the_current_lexsift_profile(vocabsieve, lexsift):
    settings, datapath, _ = lexsift
    report = import_profile(vocabsieve, settings, datapath)
    with open(os.path.join(report.backup_dir, "settings.json"), encoding="utf-8") as f:
        assert json.load(f)["target_language"] == "en"
    assert sorted(os.listdir(report.backup_dir)) == ["dict.db", "records.db", "settings.json"]


def test_data_only_profile_keeps_lexsift_settings(vocabsieve, lexsift, tmp_path):
    settings, datapath, _ = lexsift
    no_settings = VocabSieveProfile(ini_settings(tmp_path / "empty.ini"), vocabsieve.datapath)
    report = import_profile(no_settings, settings, datapath)
    assert report.settings_copied == 0
    assert settings.value("target_language") == "en"
    assert "records.db" in report.copied


class Dialogs:
    "Stands in for QMessageBox: answers questions and records what was shown"
    def __init__(self, answer):
        self.answer = answer
        self.shown = []

    def install(self, monkeypatch, main):
        monkeypatch.setattr(main.QMessageBox, "question", lambda *a, **k: self.shown.append("question") or self.answer)
        monkeypatch.setattr(main.QMessageBox, "information", lambda *a, **k: self.shown.append(a[1]))
        monkeypatch.setattr(main.QMessageBox, "critical", lambda *a, **k: self.shown.append(a[1]))


@pytest.fixture
def main_module(lexsift, monkeypatch):
    from lexsift import main
    settings, datapath, _ = lexsift
    monkeypatch.setattr(main, "settings", settings)
    monkeypatch.setattr(main, "datapath", datapath)
    return main


def test_offer_without_profile(main_module, monkeypatch):
    monkeypatch.setattr(main_module, "find_vocabsieve_profile", lambda path: None)
    dialogs = Dialogs(main_module.QMessageBox.Yes)
    dialogs.install(monkeypatch, main_module)
    assert main_module.offer_vocabsieve_import(None, first_launch=True) is False
    assert dialogs.shown == []  # silent on first launch
    assert main_module.offer_vocabsieve_import(None, first_launch=False) is False
    assert dialogs.shown == ["Import VocabSieve profile"]


def test_offer_declined_changes_nothing(main_module, vocabsieve, lexsift, monkeypatch):
    settings, _, _ = lexsift
    monkeypatch.setattr(main_module, "find_vocabsieve_profile", lambda path: vocabsieve)
    Dialogs(main_module.QMessageBox.No).install(monkeypatch, main_module)
    assert main_module.offer_vocabsieve_import(None, first_launch=True) is False
    assert settings.value("target_language") == "en"


def test_offer_accepted_imports(main_module, vocabsieve, lexsift, monkeypatch):
    settings, _, _ = lexsift
    monkeypatch.setattr(main_module, "find_vocabsieve_profile", lambda path: vocabsieve)
    dialogs = Dialogs(main_module.QMessageBox.Yes)
    dialogs.install(monkeypatch, main_module)
    assert main_module.offer_vocabsieve_import(None, first_launch=True) is True
    assert dialogs.shown == ["question", "VocabSieve profile imported"]
    assert settings.value("target_language") == "de"


def test_offer_reports_failures(main_module, vocabsieve, monkeypatch):
    def broken(*args):
        raise sqlite3.OperationalError("database is locked")
    monkeypatch.setattr(main_module, "find_vocabsieve_profile", lambda path: vocabsieve)
    monkeypatch.setattr(main_module, "import_profile", broken)
    dialogs = Dialogs(main_module.QMessageBox.Yes)
    dialogs.install(monkeypatch, main_module)
    assert main_module.offer_vocabsieve_import(None, first_launch=False) is False
    assert dialogs.shown == ["question", "Import failed"]
