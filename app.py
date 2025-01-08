import sys
from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from PySide6.QtWidgets import QApplication, QMainWindow

import live2d.v3 as live2d

from src.dialog import InputDialog
from src.live2dwidget import Live2dWidget
from src.chat_window import ChatWindow

res_folder = Path(__file__).parent / "resources"


class MainWindow(QMainWindow):

    def __init__(self, model=None, background=None):
        super().__init__()
        self.setGeometry(100, 100, 1280, 720)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.setAttribute(Qt.WidgetAttribute.WA_NoSystemBackground, False)
        self.resize(1280, 720)
        self.live2d = Live2dWidget(self, model=model, background=background)
        self.chatwindow = ChatWindow(res_folder / "miku_avatar.jpg",
                                     res_folder / "luka_avatar.png")
        self.is_chatwindow = False
        self.input_dialog = InputDialog(self)
        self.input_dialog.resize(1100, 250)
        self.input_dialog.move((self.width() - self.input_dialog.width()) // 2,
                               (self.height() - self.input_dialog.height()))
        self.menuBar().addAction("查看整体对话", self.chat_window_convert)
        self.chatwindow_point = None

    def chat_window_convert(self):
        if self.chatwindow.isVisible():
            self.chatwindow_point = self.chatwindow.geometry().topLeft()
            self.chatwindow.close()
            self.is_chatwindow = False
        else:
            if self.chatwindow_point is not None:
                self.chatwindow.move(self.chatwindow_point)
            self.chatwindow.show()
            self.is_chatwindow = True
            self.closeEvent

    def closeEvent(self, event):
        if self.chatwindow.isVisible():
            self.chatwindow_point = self.chatwindow.geometry().topLeft()
            self.chatwindow.close()
            self.is_chatwindow = False


if __name__ == "__main__":

    live2d.init()
    live2d.setLogEnable(True)

    app = QApplication(sys.argv)
    app.font().setHintingPreference(QFont.HintingPreference.PreferFullHinting)
    main_window = MainWindow(model=res_folder /
                             "miku_pro_jp/runtime/miku_sample_t04.model3.json",
                             background=res_folder / "schoolroomhibig130901.jpg")
    main_window.show()
    app.exec()

    live2d.dispose()

    # 删除音频资源
    audio_file = Path("test.wav")
    audio_file.unlink(missing_ok=True)
