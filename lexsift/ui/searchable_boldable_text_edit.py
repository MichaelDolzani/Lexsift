from .searchable_text_edit import SearchableTextEdit
from ..global_names import logger
import html
import re


class SearchableBoldableTextEdit(SearchableTextEdit):
    def unbold(self):
        self.setPlainText(self.toPlainText().replace('__', ''))

    def bold(self, word):
        logger.debug(f'bolding {word}')
        bolded_sentence = re.sub(r'\b' + re.escape(word) + r'\b', '__' + word + '__', self.toPlainText())
        self.setPlainText(bolded_sentence)

        bolded_word = '__' + word
        cursor = self.textCursor()
        cursor.setPosition(bolded_sentence.rfind(bolded_word) + len(bolded_word))
        self.setTextCursor(cursor)

    def toAnki(self):
        # The sentence is plain text (often copied from a web page), so escape it before adding markup
        result = html.escape(self.toPlainText(), quote=False)
        # substitute __word__ with <b>word</b>
        result = re.sub(r'__(.*?)__', r'<b>\1</b>', result)
        # substitute newlines with <br>
        result = result.replace('\n', '<br>')
        return result
