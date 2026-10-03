from ast import parse
from flask import Flask, abort, render_template, flash, request, redirect, url_for, send_from_directory
from werkzeug.security import safe_join
from waitress import serve
from requests import get
import os
import re
from ..global_names import settings
from .utils import getEpubMetadata
from PyQt5.QtCore import QCoreApplication, QObject
DEBUGGING = None
if os.environ.get("LEXSIFT_DEBUG"):
    DEBUGGING = True
    QCoreApplication.setApplicationName(
        "Lexsift" + os.environ.get("LEXSIFT_DEBUG", ""))
else:
    QCoreApplication.setApplicationName("Lexsift")
QCoreApplication.setOrganizationName("Lexsift")

app = Flask(__name__)


class ReaderServer(QObject):
    def __init__(self, parent, host, port):
        super().__init__()
        self.host = host
        self.port = port
        self.parent = parent

    def start_api(self):
        """ Main server application """

        @app.route("/home")
        @app.route("/")
        def home():
            books_dir = settings.value("books_dir")
            book_files = []
            books = []
            if books_dir:
                for file in os.listdir(books_dir):
                    if file.endswith(".epub"):
                        book_files.append(file)
            for book in book_files:
                metadata = getEpubMetadata(os.path.join(books_dir, book))
                metadata['path'] = book
                books.append(metadata)
            return render_template('home.html', books=books)

        @app.route('/read/<path:path>')
        def read_epub(path):
            books_dir = settings.value("books_dir")
            if not books_dir:
                return "No books directory set"
            # Only read books inside the books folder, not any path the URL names
            book_path = safe_join(books_dir, path)
            if book_path is None or not os.path.isfile(book_path):
                abort(404)
            book_url = url_for('send_epub', path=path)
            metadata = getEpubMetadata(book_path)
            return render_template('read.html',
                                   book_url=book_url,
                                   book_title=metadata['title'],
                                   book_author=metadata['author'])

        @app.route('/books/<path:path>')
        def send_epub(path):
            books_dir = settings.value("books_dir")
            if not books_dir:
                return "No books directory set"
            return send_from_directory(books_dir, path)

        serve(app, host=self.host, port=self.port)
