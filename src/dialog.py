import random
from pathlib import Path
from typing import Callable

from PySide6.QtCore import Qt
from PySide6.QtGui import QKeyEvent
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QPlainTextEdit,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from .client import TTS, Chat
from .live2dwidget import Live2dWidget


class CustomPlainTextEdit(QPlainTextEdit):
    """自定义 QPlainTextEdit，可以区分回车行为"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.use_ctrl_enter_to_send = False  # 控制发送行为的变量
        self.send_message_signal: Callable | None = None  # 发送消息的回调函数

    def keyPressEvent(self, event: QKeyEvent):
        # 如果是回车或 Ctrl+回车
        if event.key() not in [Qt.Key.Key_Return, Qt.Key.Key_Enter]:
            super().keyPressEvent(event)
            return

        if self.use_ctrl_enter_to_send:
            # Ctrl+回车发送消息，普通回车换行
            if event.modifiers() == Qt.KeyboardModifier.ControlModifier:
                if self.send_message_signal:
                    self.send_message_signal()
            else:
                super().keyPressEvent(event)  # 执行换行
        else:
            # 普通回车发送消息，Ctrl+回车换行
            if event.modifiers() == Qt.KeyboardModifier.ControlModifier:
                event.setModifiers(Qt.KeyboardModifier.NoModifier)
                super().keyPressEvent(event)  # 执行换行
            else:
                if self.send_message_signal:
                    self.send_message_signal()


class InputDialog(QWidget):

    def __init__(self, parent):
        super().__init__(parent)
        self.init_ui()

        self.chat = Chat(app_id="f465fd78-aa59-4011-af81-2192a46038f2")
        self.chat.result_signal.connect(self.conversation_callback)
        self.tts = TTS(app_id="f465fd78-aa59-4011-af81-2192a46038f2")
        self.tts.result_signal.connect(self.tts_callback)

        self.live2d: Live2dWidget = parent.live2d
        
        qss_file = Path(__file__).parent / "dialog.qss"
        self.setStyleSheet(qss_file.read_text("UTF-8"))

    def init_ui(self):
        # 设置窗口无边框和透明背景
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        # 垂直布局
        vbox = QVBoxLayout()
        vbox.setContentsMargins(20, 20, 20, 20)

        # 添加对话角色标签
        self.role_label = QLabel("Player:")
        self.role_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
        vbox.addWidget(self.role_label)

        # 输入框（透明背景）
        self.input_field = CustomPlainTextEdit()
        self.input_field.setPlaceholderText("请输入内容...")
        self.input_field.send_message_signal = self.send_message  # 绑定发送消息的回调
        vbox.addWidget(self.input_field)

        button_layout = QHBoxLayout()

        self.action_button = QPushButton("发送")
        self.action_button.clicked.connect(self.toggle_action)
        button_layout.addWidget(self.action_button)

        self.reset_button = QPushButton("重置对话")
        self.reset_button.clicked.connect(self.reset_conversation)
        button_layout.addWidget(self.reset_button)
        vbox.addLayout(button_layout)

        self.setLayout(vbox)

        # 角色对话状态
        self.is_player_turn = True  # 是否是 Player 的回合

    def toggle_action(self):
        """按钮的点击行为：发送消息或继续对话"""
        if self.is_player_turn:
            self.send_message()
        else:
            self.continue_conversation()

    def send_message(self):
        """发送消息并切换到 Miku 回复"""
        player_message = self.input_field.toPlainText().strip()
        if player_message:
            self.input_field.setPlainText(f"少女思考中...\n{player_message}")
            self.input_field.setReadOnly(True)
            self.chat.setText(player_message)
            self.chat.start()

            self.action_button.setText("继续对话")
            self.is_player_turn = False

    def conversation_callback(self, ret: str):
        if ret == "":
            ret = "初音不太明白你的意思😕"
        self.role_label.setText("Miku:")
        last = ret.strip()[-1]
        self.tts.setText(ret)
        self.tts.start()

        if last in "🙂😄🤯😟😳💃😕":
            self.input_field.setPlainText(ret.strip()[:-1])
            self.live2d.motion(last)
        elif last in "123":
            if ret.strip()[-2] in "🙂😄🤯😟😳💃😕":
                self.input_field.setPlainText(ret.strip()[:-2])
                self.live2d.motion(ret.strip()[-2])
        else:
            self.input_field.setPlainText(ret)

    def tts_callback(self, ret):
        if not ret:
            return
        self.live2d.playSound("test.wav")

    def continue_conversation(self):
        """继续对话并切换回 Player"""
        # 清空输入框并解锁
        self.input_field.clear()
        self.input_field.setReadOnly(False)
        if self.live2d.player.isPlaying():
            self.live2d.player.stop()

        # 切换角色为 Player
        self.role_label.setText("Player:")
        self.action_button.setText("发送")  # 改为发送按钮
        self.is_player_turn = True

    def reset_conversation(self):
        """重置会话ID"""
        ret = QMessageBox.warning(self, "警告", "你确定要重置会话ID吗",
                                  QMessageBox.StandardButton.Yes,
                                  QMessageBox.StandardButton.No)
        if ret == QMessageBox.StandardButton.Yes:
            self.chat.reset_conversation_id()
            self.conversation_callback(random.choice(["好吧，让我们聊点别的", "没事，让我们重新开始"]))
            self.input_field.clear()
            self.input_field.setReadOnly(False)
