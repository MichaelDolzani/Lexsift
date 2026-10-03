from PyQt5.QtWidgets import QListWidget, QListView, QToolButton, QVBoxLayout
from PyQt5.QtCore import QCoreApplication, pyqtSignal, QSize
from PyQt5.QtWidgets import QStyle
from typing import Optional

from ..audio_player import AudioPlayer
from ..global_names import MOD, settings
from ..models import AudioDefinition, AudioSourceGroup, Definition
import threading


class AudioSelector(QListWidget):
    # (lookup id, definition): results from an older lookup are dropped
    audio_fetched = pyqtSignal(int, object)

    def __init__(self) -> None:
        super().__init__()
        self.setMinimumHeight(50)
        self.setFlow(QListView.TopToBottom)
        self.setResizeMode(QListView.Adjust)
        self.setWrapping(True)
        self.audio_player = AudioPlayer()
        self.discard_audio_button = QToolButton(self)

        self.discard_audio_button.clicked.connect(self.clear)
        self.discard_audio_button.setToolTip(f"Discard audio [{MOD}+Shift+X]")

        icon = self.style().standardIcon(QStyle.SP_TrashIcon)
        self.discard_audio_button.setIcon(icon)

        self.current_audio_path = ""
        self.audios: dict[str, str] = {}
        self.sg: Optional[AudioSourceGroup] = None
        self._lookup_id = 0
        self.audio_fetched.connect(self.appendDefinition)
        self.connect_signals()

    def setSourceGroup(self, sg: AudioSourceGroup) -> None:
        self.sg = sg

    def getDefinitions(self, word: str) -> list[AudioDefinition]:
        if self.sg is None:
            return []
        return self.sg.define(word)

    def _define_online(self, lookup_id: int, sources: list, word: str) -> None:
        "Runs on a worker thread; only talks to the GUI through the signal"
        for source in sources:
            for definition in source.define(word):
                self.audio_fetched.emit(lookup_id, definition)

    def appendDefinition(self, lookup_id: int, defi: AudioDefinition):
        if lookup_id != self._lookup_id or defi.audios is None:
            return
        new_names = [name for name in defi.audios if name not in self.audios]
        self.audios.update(defi.audios)
        self.updateAudioUI(new_names)

    def clear(self):
        super().clear()
        self.audios = {}
        self.current_audio_path = ""

    def lookup(self, word: str):
        self.clear()
        self._lookup_id += 1
        if self.sg is None:
            return
        # Local sources share the main thread's sqlite cursor, so query them here (they are fast).
        # Online sources can take seconds, so query them on a worker thread.
        online = [source for source in self.sg.sources if source.INTERNET]
        for source in self.sg.sources:
            if not source.INTERNET:
                for definition in source.define(word):
                    self.appendDefinition(self._lookup_id, definition)
        if online:
            threading.Thread(target=self._define_online, args=(self._lookup_id, online, word), daemon=True).start()

    def play_audio_if_exists(self, x):
        if x is not None:
            audio_name = x.text()[2:]
            self.current_audio_path = self.audios.get(audio_name, "")
            self.play_audio(audio_name)
        else:
            self.current_audio_path = ""

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.alignDiscardButton()

    def alignDiscardButton(self):
        padding = QSize(5, 5)  # optional
        newSize = self.size() - self.discard_audio_button.size() - padding
        self.discard_audio_button.move(newSize.width(), 0)

    def updateAudioUI(self, new_names: list[str]):
        for item in new_names:
            self.addItem("🔊 " + item)
        self.setCurrentItem(self.item(0))

    def play_audio(self, name: Optional[str]) -> None:
        QCoreApplication.processEvents()
        if name is None:
            return

        self.audio_path = self.audio_player.play_audio(name, self.audios, settings.value("target_language", "en"))

    def connect_signals(self):
        self.currentItemChanged.connect(self.play_audio_if_exists)
        self.itemDoubleClicked.connect(self.play_audio_if_exists)
