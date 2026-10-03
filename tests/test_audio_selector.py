import threading
import time

from PyQt5.QtCore import QCoreApplication

from lexsift.models import AudioDefinition, AudioSourceGroup
from lexsift.ui.audio_selector import AudioSelector


class FakeSource:
    def __init__(self, name, internet, audios, delay=0.0):
        self.name = name
        self.INTERNET = internet
        self.audios = audios
        self.delay = delay
        self.threads = []

    def define(self, word, no_lemma=False):
        self.threads.append(threading.current_thread())
        time.sleep(self.delay)
        return [AudioDefinition(headword=word, lookup_term=word, source=self.name,
                                audios={f"{self.name}::{word}::{a}": a for a in self.audios})]


def wait_for(condition, timeout=5.0):
    deadline = time.time() + timeout
    while not condition() and time.time() < deadline:
        QCoreApplication.processEvents()
        time.sleep(0.01)
    QCoreApplication.processEvents()


def labels(selector):
    return [selector.item(i).text() for i in range(selector.count())]


def make_selector(*sources):
    selector = AudioSelector()
    selector.play_audio = lambda name: None  # don't play anything in tests
    selector.setSourceGroup(AudioSourceGroup(list(sources)))
    return selector


def test_online_sources_run_off_the_gui_thread_and_local_ones_on_it():
    local = FakeSource("local", internet=False, audios=["a"])
    online = FakeSource("forvo", internet=True, audios=["b"])
    selector = make_selector(local, online)
    selector.lookup("hund")
    wait_for(lambda: selector.count() == 2)
    assert local.threads == [threading.main_thread()]
    assert online.threads and online.threads[0] is not threading.main_thread()


def test_no_duplicate_entries_with_several_sources():
    selector = make_selector(FakeSource("one", False, ["a"]), FakeSource("two", False, ["b", "c"]))
    selector.lookup("katt")
    assert labels(selector) == ["🔊 one::katt::a", "🔊 two::katt::b", "🔊 two::katt::c"]


def test_results_of_a_previous_lookup_are_dropped():
    slow = FakeSource("forvo", internet=True, audios=["x"], delay=0.3)
    selector = make_selector(slow)
    selector.lookup("first")
    slow.delay = 0.0
    selector.lookup("second")
    wait_for(lambda: len(slow.threads) == 2, timeout=2)
    wait_for(lambda: False, timeout=0.5)  # let the slow first reply arrive
    assert labels(selector) == ["🔊 forvo::second::x"]
