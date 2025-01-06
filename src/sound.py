from PySide6.QtCore import QObject
from PySide6.QtMultimedia import QMediaPlayer, QAudioOutput
from PySide6.QtCore import QUrl

class SoundPlayer(QMediaPlayer):

    def __init__(self, parent: QObject | None = None) -> None:
        super().__init__(parent)
        self.audioOutput_ = QAudioOutput()
        self.setAudioOutput(self.audioOutput_)
        self.audioOutput_.setVolume(50)
    
    def play_file(self, file: str):
        self.setSource(QUrl.fromLocalFile(file))
        self.play()