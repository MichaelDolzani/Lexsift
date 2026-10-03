import pytest
from lexsift.local_dictionary import LocalDictionary


def test_local_dictionary(tmp_path):
    db = LocalDictionary(tmp_path)
    print(tmp_path)
    assert db.countDicts() == 0
    db.importdict({"test": "a test is a test"}, "de", "test-dict")
    assert db.countDicts() == 1
    assert db.define("test", "de", "test-dict") == "a test is a test"
    db.deletedict("test-dict")
    assert db.countDicts() == 0


def test_import_stardict_normal(tmp_path):
    db = LocalDictionary(tmp_path)
    assert db.countDicts() == 0
    db.dictimport("testdata/stardict/quick_eng-rus-2.4.2/quick_english-russian.ifo",
                  dicttype="stardict",
                  lang="en",
                  name="quick_eng-rus-2.4.2")
    assert db.countDicts() == 1
    assert db.define("abdominous", "en", "quick_eng-rus-2.4.2") == "толстый"
    assert db.define("loophole", "en", "quick_eng-rus-2.4.2") == "бойница"
    assert db.define("luggage", "en", "quick_eng-rus-2.4.2") == "багаж"


def test_import_stardict_xdxf(tmp_path):
    db = LocalDictionary(tmp_path)
    assert db.countDicts() == 0
    db.dictimport("testdata/stardict/stardict-FR-LingvoUniversal-2.4.2/FR-Universal.ifo",
                  dicttype="stardict",
                  lang="fr",
                  name="fr-universal")
    assert db.countDicts() == 1
    assert db.define("accouchement", "fr", "fr-universal") == '''<i>m</i>
 1) р'оды
  accouchement avant terme, accouchement prématuré — преждевр'еменные р'оды
  accouchement après terme, accouchement tardif — запозд'алые р'оды
  accouchement sans douleur — обезб'оливание р'одов
  douleurs de l'accouchement — родов'ые б'оли
 2) <i>перен.</i> дл'ительное созрев'ание, тр'удное осуществл'ение'''
    assert db.define("persévérant", "fr", "fr-universal") == '''<i>adj</i>, <i>subst</i> (<i>fém</i> - persévérante)
 1) наст'ойчивый [наст'ойчивая], уп'орный [уп'орная]; твёрдый [твёрдая]
 2) посто'янный [посто'янная]'''
    assert db.define("pièce-raccord", "fr", "fr-universal") == '''pièce-raccord
 <i>m</i>
 <i>(pl s + s</i> ) соедин'ительная часть, соедин'ительная дет'аль'''


def test_import_dsl(tmp_path):
    db = LocalDictionary(tmp_path)
    assert db.countDicts() == 0
    # Same entries, as UTF-8 with a BOM and as gzipped UTF-16
    db.dictimport("testdata/dsl/ru_en.dsl", dicttype="dsl", lang="ru", name="dsl_test")
    db.dictimport("testdata/dsl/ru_en.dsl.dz", dicttype="dsl", lang="ru", name="dsl_test2")
    assert db.countDicts() == 2
    for name in ("dsl_test", "dsl_test2"):
        # First entry: the header must not swallow it
        assert db.define("зубчатый", "ru", name) == "serrated, toothed"
        assert db.define("лиственный", "ru", name) == "broadleaf; deciduous; leafy"
        assert db.define("эмиграция", "ru", name) == \
            "ж.<br>1) emigration<br>жить в эмиграция — live as an emigrant<br>2) emigrants pl"
        # Last entry: must not be dropped
        assert db.define("окорять", "ru", name) == "bark, peel"


def test_import_cognates(tmp_path):
    db = LocalDictionary(tmp_path)
    assert db.countDicts() == 0
    db.dictimport("testdata/cognates/cognates.json.gz",
                  dicttype="cognates",
                  lang="<all>",
                  name="cognates"
                  )
    assert db.countDicts() == 1
    assert db.define("chodník", "cs", "cognates") == '''["sk", "pl"]'''
    assert db.define("apple", "en", "cognates") == '''["nl", "de", "sv"]'''
    assert db.define("tragisch", "de", "cognates") == '''["nl", "en", "fr"]'''


def test_kaikki(tmp_path):
    db = LocalDictionary(tmp_path)
    assert db.countDicts() == 0
    db.dictimport("testdata/kaikki/mixed_short.jsonl",
                  dicttype="wiktdump",
                  lang="sv",
                  name="kaikki-swedish"
                  )
    assert db.countDicts() == 1
    assert db.define("affektionsvärde", "sv", "kaikki-swedish") == (
        "<i>Noun</i> <br>\n<strong>affektionsvärde n</strong><br>\n<br>\n1. sentimental value")
    # Entries with the same headword are merged
    assert db.define("rådigt", "sv", "kaikki-swedish") == (
        "<i>Adj</i> <br>\n<strong>rådigt</strong><br>\n<br>\n1. indefinite neuter singular of rådig"
        "\n\n"
        "<i>Adv</i> <br>\n<strong>rådigt (comparative rådigare)</strong><br>\n<br>\n1. resourcefully, resolutely")
    # Entries in other languages are skipped
    with pytest.raises(KeyError):
        db.define("géminer", "sv", "kaikki-swedish")

    db.dictimport("testdata/kaikki/mixed_short.jsonl",
                  dicttype="wiktdump",
                  lang="fr",
                  name="kaikki-french"
                  )
    assert db.countDicts() == 2
    assert db.define("géminer", "fr", "kaikki-french") == (
        "<i>Verb</i> <br>\n<strong></strong><br>\n<br>\n1. Se doubler.<br>\n2. Grouper deux à deux, doubler.")
