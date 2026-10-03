from ..models import DictionarySource, LookupResult, SourceOptions
from urllib.parse import quote
from ..cached_get import cached_get


class GoogleTranslateSource(DictionarySource):
    def __init__(self, langcode: str, options: SourceOptions, gtrans_api: str, gtrans_to_langcode: str) -> None:
        super().__init__("Google Translate", langcode, options)
        # Lingva/Google still use the old code for Hebrew. Keep self.langcode as is: it drives lemmatization.
        self.api_langcode = "iw" if langcode == "he" else langcode
        self.gtrans_api = gtrans_api
        self.to_langcode = gtrans_to_langcode

    def _lookup(self, word: str) -> LookupResult:
        url = f"{self.gtrans_api}/api/v1/{self.api_langcode}/{self.to_langcode}/{quote(word)}"
        try:
            res = cached_get(url)
            return LookupResult(definition=res.json()['translation'])
        except Exception as e:  # network errors, error pages that are not JSON, JSON without a translation
            return LookupResult(error=repr(e))
