from PySide6.QtCore import QObject, QThread, Signal
import appbuilder
from appbuilder.core.message import Message
from pathlib import Path


class Chat(QThread):
    result_signal = Signal(str)

    def __init__(self,
                 parent: QObject | None = None,
                 app_id: str | None = None) -> None:
        super().__init__(parent)
        if app_id is None:
            raise ValueError("Cannot find app_id")
        self.client = appbuilder.AppBuilderClient(app_id)
        self.conversation_id = self.client.create_conversation()
        self.text = ""

    def reset_conversation_id(self):
        self.conversation_id = self.client.create_conversation()

    def setText(self, text: str):
        self.text = text

    def run(self):
        try:
            ret = self.client.run(self.conversation_id, self.text)
            assert ret.content is not None
            self.result_signal.emit(ret.content.answer)
        except Exception as e:
            self.result_signal.emit('Error: ' + str(e))


class TTS(QThread):
    result_signal = Signal(bool)

    def __init__(self,
                 parent: QObject | None = None,
                 app_id: str | None = None,
                 save_path: str = "test.wav") -> None:
        super().__init__(parent)
        if app_id is None:
            raise ValueError("Cannot find app_id")
        self.client = appbuilder.TTS(app_id)
        self.save_path = save_path

    def setText(self, text: str):
        self.text = text

    def run(self):
        try:
            ret = self.client.run(Message({"text": self.text}),
                                  person=4144, # 度禧禧
                                  audio_type="wav")
            assert ret.content is not None
            Path(self.save_path).write_bytes(ret.content["audio_binary"])
            self.result_signal.emit(True)
        except Exception as e:
            self.result_signal.emit(False)
