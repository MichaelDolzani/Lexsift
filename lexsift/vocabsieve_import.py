"Import settings and data from an existing VocabSieve profile"
import json
import os
import shutil
import sqlite3
from contextlib import closing
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Optional

from loguru import logger
from PyQt5.QtCore import QSettings

VOCABSIEVE_ORGANIZATION = "FreeLanguageTools"
VOCABSIEVE_APPLICATION = "VocabSieve"
DATABASES = ("records.db", "dict.db")
FOLDERS = ("forvo", "images")


@dataclass
class VocabSieveProfile:
    settings: QSettings
    datapath: str

    def describe(self) -> str:
        "Short summary of what the profile contains, for confirmation dialogs"
        parts = []
        if keys := self.settings.allKeys():
            parts.append(f"{len(keys)} settings")
        parts.extend(name for name in DATABASES + FOLDERS if os.path.exists(os.path.join(self.datapath, name)))
        return ", ".join(parts)


@dataclass
class ImportReport:
    backup_dir: str
    settings_copied: int = 0
    copied: list[str] = field(default_factory=list)


def vocabsieve_datapath(lexsift_datapath: str) -> str:
    "VocabSieve's data folder, derived from Lexsift's"
    # QStandardPaths.DataLocation is <base>/<organization>/<application> on every platform
    base = os.path.dirname(os.path.dirname(os.path.normpath(lexsift_datapath)))
    return os.path.join(base, VOCABSIEVE_ORGANIZATION, VOCABSIEVE_APPLICATION)


def find_vocabsieve_profile(lexsift_datapath: str) -> Optional[VocabSieveProfile]:
    "Return the VocabSieve profile on this computer, or None if VocabSieve was never used"
    profile = VocabSieveProfile(QSettings(VOCABSIEVE_ORGANIZATION, VOCABSIEVE_APPLICATION),
                                vocabsieve_datapath(lexsift_datapath))
    return profile if profile.describe() else None


def _copy_database(src: str, dst: str) -> None:
    # The backup API gives a consistent copy even if VocabSieve is running,
    # and writes safely into a destination that Lexsift itself has open
    with closing(sqlite3.connect(Path(src).absolute().as_uri() + "?mode=ro", uri=True)) as source, \
            closing(sqlite3.connect(dst, timeout=10)) as destination:
        source.backup(destination)


def _rewrite_note_paths(records_db: str, old_datapath: str, new_datapath: str) -> None:
    "Notes store absolute image and audio paths; point them at the copies in Lexsift's folder"
    old_prefix = os.path.join(old_datapath, "")
    new_prefix = os.path.join(new_datapath, "")
    with closing(sqlite3.connect(records_db, timeout=10)) as conn, conn:  # closes, and commits on success
        if not conn.execute("SELECT 1 FROM sqlite_master WHERE type='table' AND name='notes'").fetchone():
            return
        for column in ("image", "pronunciation"):
            conn.execute(f"""
                UPDATE notes SET {column} = :new || substr({column}, :start)
                WHERE substr({column}, 1, :length) = :old
                """, {"new": new_prefix, "old": old_prefix, "start": len(old_prefix) + 1, "length": len(old_prefix)})


def _backup_lexsift(settings: QSettings, datapath: str) -> str:
    backup_dir = os.path.join(datapath, "backups",
                              "before-vocabsieve-import-" + datetime.now().strftime("%Y-%m-%d-%H-%M-%S"))
    os.makedirs(backup_dir)
    with open(os.path.join(backup_dir, "settings.json"), "w", encoding="utf-8") as f:
        json.dump({key: settings.value(key) for key in settings.allKeys()}, f, indent=2, default=str)
    for name in DATABASES:
        if os.path.exists(path := os.path.join(datapath, name)):
            _copy_database(path, os.path.join(backup_dir, name))
    return backup_dir


def import_profile(profile: VocabSieveProfile, settings: QSettings, datapath: str) -> ImportReport:
    """Replace Lexsift's settings and data with the VocabSieve profile's.
    Lexsift's current settings and databases are backed up first."""
    report = ImportReport(backup_dir=_backup_lexsift(settings, datapath))
    logger.info(f"Backed up Lexsift profile to {report.backup_dir}")

    if keys := profile.settings.allKeys():
        settings.clear()
        for key in keys:
            settings.setValue(key, profile.settings.value(key))
        settings.sync()
        report.settings_copied = len(keys)

    for name in DATABASES:
        if os.path.exists(src := os.path.join(profile.datapath, name)):
            _copy_database(src, os.path.join(datapath, name))
            report.copied.append(name)
    if "records.db" in report.copied:
        _rewrite_note_paths(os.path.join(datapath, "records.db"), profile.datapath, datapath)

    for name in FOLDERS:
        if os.path.isdir(src := os.path.join(profile.datapath, name)):
            shutil.copytree(src, os.path.join(datapath, name), dirs_exist_ok=True)
            report.copied.append(name)

    logger.info(f"Imported VocabSieve profile from {profile.datapath}: "
                f"{report.settings_copied} settings, {report.copied}")
    return report
