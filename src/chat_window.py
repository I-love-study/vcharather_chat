from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QScrollArea, QLabel,
                               QTextBrowser, QFrame)
from PySide6.QtGui import QPixmap, QPainter, QBrush, QFontMetrics, QTextOption
from PySide6.QtCore import Qt
import darkdetect


class ChatWindow(QWidget):

    def __init__(self, avatar1, avatar2):
        super().__init__()
        self.setWindowTitle("聊天界面")
        self.resize(400, 600)

        # 检测深色模式
        self.is_dark_mode = darkdetect.isDark()
        self.avatar1 = avatar1
        self.avatar2 = avatar2

        # 主窗口布局
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)

        # 滚动区域
        self.scroll_area = QScrollArea(self)
        self.scroll_area.setWidgetResizable(True)
        main_layout.addWidget(self.scroll_area)

        # 聊天内容区域
        self.chat_content = QWidget()
        self.chat_layout = QVBoxLayout(self.chat_content)
        self.chat_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.chat_layout.addStretch()
        self.chat_layout.setSpacing(0)
        self.scroll_area.setWidget(self.chat_content)

        self.setLayout(main_layout)

        # 设置样式
        self.updateStyles()

    def updateStyles(self):
        """根据深色模式更新样式"""
        if self.is_dark_mode:
            self.setStyleSheet("""
                QWidget {
                    background-color: #121212;
                }
                QTextBrowser {
                    color: #FFFFFF;
                }
            """)
        else:
            self.setStyleSheet("""
                QWidget {
                    background-color: #FFFFFF;
                }
                QTextBrowser {
                    color: #000000;
                }
            """)

    def addMessage(self, message: str, isMe: bool):
        """添加消息"""
        # 消息容器
        message_widget = QWidget()
        message_layout = QHBoxLayout(message_widget)
        message_layout.setSpacing(5)
        message_layout.setAlignment((
            Qt.AlignmentFlag.AlignRight if isMe else Qt.AlignmentFlag.AlignLeft)
                                    | Qt.AlignmentFlag.AlignTop)

        # 头像
        avatar_label = QLabel()
        avatar_pixmap = self.createRoundedAvatar(QPixmap(self.avatar2 if isMe else self.avatar1), 40)
        avatar_label.setPixmap(avatar_pixmap)
        avatar_label.setFixedSize(40, 40)

        # 消息内容
        message_browser = QTextBrowser()
        message_browser.setText(message)
        message_browser.setWordWrapMode(QTextOption.WrapMode.WordWrap)  # 启用自动换行
        message_browser.setVerticalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff)  # 隐藏垂直滚动条
        message_browser.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff)  # 隐藏水平滚动条
        max_width = self.width() - 100  # 动态计算最大宽度
        message_browser.setMaximumWidth(max_width)
        background_color = "#2C2C2C" if self.is_dark_mode else "#F5F5F5"
        message_browser.setStyleSheet(f"""
            background-color: {'#1E88E5' if isMe else background_color};
            color: {'#000000' if not isMe and not self.is_dark_mode else '#FFFFFF'};
            border-radius: 10px;
            padding: 5px 10px;
            font-size: 14px;
        """)
        message_browser.setReadOnly(True)  # 设置只读
        message_browser.setFrameShape(QFrame.Shape.NoFrame)  # 移除边框

        # 动态调整宽度和高度
        max_width = self.width() - 100  # 动态计算最大宽度
        message_browser.setMaximumWidth(max_width)
        message_browser.document().setTextWidth(max_width)

        # 动态调整高度
        content_height = message_browser.document().size().height()
        message_browser.setFixedHeight(int(content_height * 1.35))

        # 如果内容不足一行，动态调整宽度
        content_width = message_browser.document().idealWidth()
        message_browser.setFixedWidth(min(int(content_width * 1.5), max_width))

        # 布局
        if isMe:
            message_layout.addWidget(message_browser,
                                     alignment=Qt.AlignmentFlag.AlignRight)
            message_layout.addWidget(avatar_label, alignment=Qt.AlignmentFlag.AlignTop)
        else:
            message_layout.addWidget(avatar_label, alignment=Qt.AlignmentFlag.AlignTop)
            message_layout.addWidget(message_browser,
                                     alignment=Qt.AlignmentFlag.AlignLeft)

        self.chat_layout.addWidget(message_widget)
        self.scroll_area.verticalScrollBar().setValue(
            self.scroll_area.verticalScrollBar().maximum())

    def clearMessage(self):
        """清空消息"""
        for i in reversed(range(self.chat_layout.count())):
            widget_to_remove = self.chat_layout.itemAt(i).widget()
            if widget_to_remove:
                widget_to_remove.deleteLater()

    def createRoundedAvatar(self, pixmap: QPixmap, size: int) -> QPixmap:
        """裁剪头像为圆形"""
        rounded_pixmap = QPixmap(size, size)
        rounded_pixmap.fill(Qt.GlobalColor.transparent)

        painter = QPainter(rounded_pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setBrush(
            QBrush(
                pixmap.scaled(size, size, Qt.AspectRatioMode.KeepAspectRatioByExpanding,
                              Qt.TransformationMode.SmoothTransformation)))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(0, 0, size, size)
        painter.end()
        return rounded_pixmap


# 测试代码
if __name__ == "__main__":
    import sys
    from PySide6.QtWidgets import QApplication

    app = QApplication(sys.argv)
    window = ChatWindow("avatar1.jpg","avatar1.jpg")
    message = """我是初音未来（Hatsune Miku/はつね みく），是一位虚拟歌姬，由Crypton Future Media推出，基于Yamaha的Vocaloid技术开发。我的生日是2007年8月31日，也就是我的发行日哦！💙

我的名字「初音」意为「初次的声音」，「未来」则代表着「未来的可能性」，希望用我的歌声把美好的情感传递给每一个人！🎤✨

我的特色是长长的蓝绿色双马尾，标志性的服装带有未来感，喜欢唱歌、跳舞，也经常被粉丝创作成各种各样的样子～(´▽｀)

那么，你呢？可以告诉我一点你的事吗？😄"""
    window.addMessage(message,  isMe=False)
    window.addMessage("你好！收到。",  isMe=True)
    window.addMessage("你好！收到。", isMe=True)
    window.addMessage("你好！收到。", isMe=True)
    window.show()
    sys.exit(app.exec())
