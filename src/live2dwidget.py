import os

import OpenGL.GL as gl
from PySide6.QtCore import QPoint, Qt, QTimerEvent, QUrl
from PySide6.QtGui import QGuiApplication, QImage, QPainter, QMouseEvent, QCursor
from PySide6.QtOpenGLWidgets import QOpenGLWidget
from PySide6.QtWidgets import QWidget
from PySide6.QtMultimedia import QMediaPlayer, QAudioOutput

import live2d.v3 as live2d
from live2d.utils.lipsync import WavHandler

from .sound import SoundPlayer

def callback():
    print("motion end")


class Live2dWidget(QOpenGLWidget):

    def __init__(self,
                 parent: QWidget | None = None,
                 model: os.PathLike | str | None = None,
                 background: os.PathLike | str | None = None) -> None:
        super().__init__(parent)
        self.isInLA = False
        self.clickInLA = False
        self.model_path = model
        #self.setWindowFlags(Qt.WindowType.FramelessWindowHint)

        #self.setAttribute(Qt.WidgetAttribute.WA_AlwaysStackOnTop)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        #self.setWindowFlags(Qt.WindowType.SubWindow)
        self.a = 0
        self.resize(1280, 720)
        self.read = True
        self.clickX = -1
        self.clickY = -1
        self.model: live2d.LAppModel
        self.setObjectName("Live2d")
        self.systemScale = QGuiApplication.primaryScreen().devicePixelRatio()

        if background is not None:
            self.loadPicFile(background)

        # 初始化播放器
        self.player = SoundPlayer()
        self.player.playbackStateChanged.connect(self.on_mediapalyer_status_changed)

        # 初始化 WavHandler
        self.wav_handler = WavHandler()
        self.lip_sync_factor = 2.5  # 控制嘴巴张合幅度

    def loadPicFile(self, picFile):
        self.picFile = str(picFile)
        self.img = QImage()
        self.img.load(self.picFile)

    def initializeGL(self) -> None:
        # 将当前窗口作为 OpenGL 的上下文
        # 图形会被绘制到当前窗口
        self.makeCurrent()
        live2d.glewInit()

        # 创建模型
        self.model = live2d.LAppModel()
        self.model.SetAutoBreathEnable(True)
        self.model.SetAutoBlinkEnable(True)

        self.model.LoadModelJson(str(self.model_path))

        # 以 fps = 30 的频率进行绘图
        self.startTimer(int(1000 / 30))

    def resizeGL(self, w: int, h: int) -> None:
        # 使模型的参数按窗口大小进行更新
        if self.model:
            self.model.Resize(w, h)

    def paintGL(self) -> None:
        gl.glClearColor(0.0, 0.0, 0.0, 0.0)
        gl.glClear(gl.GL_COLOR_BUFFER_BIT)
        live2d.clearBuffer()

        self.model.Update()
        if self.img:
            paint = QPainter()
            paint.begin(self)
            paint.drawImage(QPoint(0, 0), self.img)
            paint.end()
        #gl.texture

        if self.wav_handler.Update():
            rms = self.wav_handler.GetRms()
            self.model.AddParameterValue(live2d.StandardParams.ParamMouthOpenY,
                                         rms * self.lip_sync_factor)

        self.model.Draw()

    def timerEvent(self, a0: QTimerEvent | None) -> None:
        if not self.isVisible():
            return

        self.update()

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        x, y = event.scenePosition().x(), event.scenePosition().y()
        self.model.Drag(int(self.x() + x), int(self.y() + y))

    def on_mediapalyer_status_changed(self, status):
        if status == QMediaPlayer.PlaybackState.StoppedState:
            print(status)
            self.wav_handler.pcmData = None # type: ignore
            #if self.wav_file is not None:
            #    Path(self.wav_file).unlink(True)
            self.model.StartMotion("Idle", 0, 2)

    def playSound(self, wav_file: str) -> None:
        self.player.play_file(wav_file)
        self.wav_handler.Start(wav_file)

    def motion(self, emoji: str):
        emoji_dict = {
            "🙂": ["Idle", 1],
            "😄": ["Idle", 2],
            "🤯": ["Tap", 0],
            "😟": ["Tap", 1],
            "😳": ["Flick", 0],
            "💃": ["Flick", 1],
            "😕": ["FlickUp", 0],
        }
        self.model.StartMotion(*emoji_dict[emoji], priority=1)


if __name__ == "__main__":
    from pathlib import Path
    import sys
    from PySide6.QtWidgets import QApplication

    live2d.init()
    live2d.setLogEnable(True)

    res_folder = Path(__file__).parent.parent / "resources"

    app = QApplication(sys.argv)
    main_window = Live2dWidget(model=res_folder /
                             "miku_pro_jp/runtime/miku_sample_t04.model3.json",
                             background=res_folder / "schoolroomhibig130901.jpg")
    main_window.show()
    app.exec()

    live2d.dispose()
