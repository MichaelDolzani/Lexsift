from lexsift.ui.searchable_boldable_text_edit import SearchableBoldableTextEdit


def to_anki(text, bold=None):
    edit = SearchableBoldableTextEdit()
    edit.setPlainText(text)
    if bold:
        edit.bold(bold)
    return edit.toAnki()


def test_bold_and_newlines():
    assert to_anki("Der Hund schläft.\nJa.", bold="Hund") == "Der <b>Hund</b> schläft.<br>Ja."


def test_plain_text_is_escaped():
    # "<" used to start an HTML tag in Anki and swallow the rest of the sentence
    assert to_anki("if a<b then b>a & done", bold="done") == "if a&lt;b then b&gt;a &amp; <b>done</b>"


def test_markup_from_web_pages_is_not_injected():
    assert to_anki('<img src=x onerror="alert(1)">') == '&lt;img src=x onerror="alert(1)"&gt;'
