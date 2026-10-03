from datetime import datetime as dt
import glob
import os
from ..global_names import logger


def get_uniques(l: list):
    return list(set(l) - set([""]))


def uniq_preserve_order(l: list) -> list:
    return sorted(set(l), key=lambda x: l.index(x))


def date_to_timestamp(datestr: str):
    return dt.strptime(datestr, "%Y-%m-%d %H:%M:%S").timestamp()


def findDBpath(path) -> str:
    # KOReader settings may be in a hidden directory
    paths = glob.glob(os.path.join(path, "**/vocabulary_builder.sqlite3"), recursive=True)\
        + glob.glob(os.path.join(path, ".*/**/vocabulary_builder.sqlite3"), recursive=True)
    if paths:
        return paths[0]
    else:
        raise FileNotFoundError("Cannot find vocabulary_builder.sqlite3")


def koreader_metadata_path(book_path: str) -> str:
    """Path of KOReader's metadata file for a book.
    KOReader strips only the last extension for the sidecar folder and uses it in the file name:
    book.epub -> book.sdr/metadata.epub.lua, book.fb2.zip -> book.fb2.sdr/metadata.zip.lua"""
    base, ext = os.path.splitext(book_path)
    return os.path.join(base + ".sdr", f"metadata{ext}.lua")


def koreader_scandir(path):
    filelist = []
    for filetype in ["epub", "fb2", "fb2.zip", "pdf"]:
        files = glob.glob(os.path.join(path, "**/*." + filetype), recursive=True)
        for filename in files:
            if os.path.exists(koreader_metadata_path(filename)):
                filelist.append(filename)
    logger.info(f"Found {len(filelist)} book files in {path}: {filelist}")
    return filelist


def findHistoryPath(path):
    # KOReader settings may be in a hidden directory
    paths = glob.glob(os.path.join(path, "**/lookup_history.lua"), recursive=True)\
        + glob.glob(os.path.join(path, ".*/**/lookup_history.lua"), recursive=True)
    if paths:
        return paths[0]
    else:
        return ""
