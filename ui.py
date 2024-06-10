import os
import subprocess
import sys
from datetime import datetime

from PyQt5.QtCore import pyqtSignal, QSize, pyqtSlot
from PyQt5.QtGui import QColor, QIcon
from PyQt5.QtWidgets import (
    QMainWindow,
    QPushButton,
    QVBoxLayout,
    QWidget,
    QLabel,
    QLineEdit,
    QProgressBar,
    QComboBox,
    QTableWidgetItem,
    QTableWidget,
    QHBoxLayout,
    QHeaderView,
    QGraphicsDropShadowEffect,
    QMessageBox,
    QTextEdit,
    QDesktopWidget,
    QMenu,
    QAction,
    QSizePolicy,
)

from core import DownloadThread


class MainWindow(QMainWindow):
    # 定义下载进度信号
    progress = pyqtSignal(int)
    # 定义下载完成信号
    finished = pyqtSignal()
    
    # 初始化方法
    def __init__(self, url, download_type):
        super().__init__()
        self.url = url
        self.download_type = download_type
        self.cookies = None
        self.success = False  # 新增success属性，用于判断下载是否成功
        # 设置yt_dlp下载选项
        self.ydl_opts = {
            "progress_hooks": [self.my_hook],
            "outtmpl": "%(title)s.%(ext)s",  # 输出文件命名规则
            "format": (
                "bestaudio/best"
                if self.download_type == "音频"
                else "bestvideo+bestaudio"
            ),
        }
    
    def set_cookies(self, cookies_path):
        """设置cookies参数"""
        self.cookies = cookies_path
    
    # 线程执行方法
    def run(self):
        # 判断本地目录是否存在cookies.txt文件
        if os.path.exists("cookies.txt"):
            self.set_cookies("cookies.txt")
            self.ydl_opts["cookiefile"] = self.cookies
        
        try:
            if self.ydl_opts.get("format") == "bestaudio/best":
                self.ydl_opts["postprocessors"] = [
                    {
                        "key": "FFmpegExtractAudio",
                        "preferredcodec": "mp3",
                        "preferredquality": "192",
                    }
                ]
            # 使用yt_dlp下载视频或音频
            with yt_dlp.YoutubeDL(self.ydl_opts) as ydl:
                # 判断下载类型，设置ydl_opts中的format参数
                ydl.extract_info(self.url, download=True)
                # ydl.download([self.url])
            self.success = True  # 下载成功时，设置success为True
        
        except yt_dlp.utils.DownloadError:
            # 下载出错时，发送完成信号
            self.finished.emit()
            print("Requested format is not available for this video.")
        else:
            # 下载成功时，发送完成信号
            self.finished.emit()
    
    def update_format(self, download_type):
        # 读取下载类型，设置ydl_opts中的format参数
        if download_type == "视频":
            self.ydl_opts["format"] = "bestvideo+bestaudio"
        else:
            self.ydl_opts["format"] = "bestaudio/best"
    
    # 自定义下载进度钩子函数
    def my_hook(self, d):
        # 当下载状态为进行中时，发送进度信号
        if d["status"] == "downloading":
            p = d["_percent_str"].replace("%", "")
            self.progress.emit(int(float(p)))
    
    # 主窗口类，继承自QMainWindow


class MainWindow(QMainWindow):
    # 初始化方法
    def __init__(self):
        super().__init__()
        self.initUI()
        self.download_thread = None
        self.load_cookies()
        
        
        # 检查cookies.txt文件是否存在
        if os.path.exists("cookies.txt"):
            # 如果存在，设置DownloadThread类的cookies参数
            self.download_thread = DownloadThread(None, None, '视频', '音频')
            self.download_thread.set_cookies("cookies.txt")
            # 读取cookies.txt文件的内容到cookies_input文本框中
            with open("cookies.txt", "r") as f:
                self.cookies_input.setPlainText(f.read())
    
    # 界面初始化方法
    def initUI(self):
        self.setWindowTitle("禹驰技术-视频下载器")  # 设置窗口标题
        # 设置窗口大小并居中显示
        desktop = QDesktopWidget()
        screen_size = desktop.availableGeometry()
        x = (screen_size.width() - 1440) // 2
        y = (screen_size.height() - 900) // 2
        self.setGeometry(x, y, 1440, 1080)
        
        layout = QVBoxLayout()
        icon_path = "download_icon.png"  # 确保这个路径指向实际存在的图标文件
        save_icon_path = "save_icon.png"  # 确保这个路径指向实际存在的图标文件
        
        url_layout = QHBoxLayout()
        url_layout.addWidget(QLabel("URL:"))
        self.url_input = QLineEdit()
        url_layout.addWidget(self.url_input)
        self.download_button = QPushButton("下载")
        self.download_button.setIcon(QIcon(icon_path))
        self.download_button.setIconSize(QSize(64, 64))
        url_layout.addWidget(self.download_button)
        self.download_button.clicked.connect(self.download)
        layout.addLayout(url_layout)
        
        download_type_layout = QHBoxLayout()
        download_type_layout.addWidget(QLabel("下载类型:"))
        self.download_type = QComboBox()
        self.download_type.addItems(["视频", "音频"])
        # 连接currentIndexChanged信号到槽函数
        self.download_type.currentIndexChanged.connect(self.update_download_type)
        # 设置选择框的尺寸策略为自适应
        self.download_type.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        download_type_layout.addWidget(self.download_type)
        download_type_layout.addStretch()  # 添加弹性空间使得选择框靠左对齐
        layout.addLayout(download_type_layout)
        
        cookies_layout = QHBoxLayout()
        cookies_layout.addWidget(QLabel("Cookies:"))
        self.cookies_input = QTextEdit()
        cookies_layout.addWidget(self.cookies_input)
        self.save_button = QPushButton("保存Cookies")
        self.save_button.setIcon(QIcon(save_icon_path))
        self.save_button.setIconSize(QSize(64, 64))
        cookies_layout.addWidget(self.save_button)
        self.save_button.clicked.connect(self.save_cookies)
        layout.addLayout(cookies_layout)
        
        # 创建一个水平布局
        progress_layout = QHBoxLayout()
        # 添加下载进度标签
        progress_layout.addWidget(QLabel("下载进度:"))
        # 创建进度条
        self.progress_bar = QProgressBar()
        # 将进度条添加到水平布局
        progress_layout.addWidget(self.progress_bar)
        # 将水平布局添加到主布局
        layout.addLayout(progress_layout)
        
        # 添加表格用于展示文件
        self.file_table = QTableWidget()
        self.file_table.setColumnCount(2)  # 两列，一列是文件名，一列是类型
        self.file_table.setHorizontalHeaderLabels(["文件名", "类型"])
        self.file_table.horizontalHeader().setSectionResizeMode(
            0, QHeaderView.ResizeMode.Stretch
        )
        self.file_table.horizontalHeader().setSectionResizeMode(
            1, QHeaderView.ResizeMode.ResizeToContents
        )
        self.file_table.mouseDoubleClickEvent = self.play_selected_file  # 双击播放
        layout.addWidget(self.file_table)
        
        # 初始化时加载当前目录下的媒体文件
        self.update_file_table()
        
        central_widget = QWidget()
        central_layout = QHBoxLayout(central_widget)
        container = QWidget()
        container.setLayout(layout)
        container.setStyleSheet("background-color: #2b2b2b; border-radius: 10px;")
        shadow_effect = QGraphicsDropShadowEffect(self)
        shadow_effect.setBlurRadius(15)
        shadow_effect.setXOffset(0)
        shadow_effect.setYOffset(0)
        shadow_effect.setColor(QColor(0, 0, 0, 80))
        container.setGraphicsEffect(shadow_effect)
        central_layout.addWidget(container)
        central_layout.setContentsMargins(10, 10, 10, 10)
        self.setCentralWidget(central_widget)
        
        self.download_button.setIcon(QIcon(icon_path))
        self.download_button.setIconSize(QSize(64, 64))
        
        self.save_button.setIcon(QIcon(save_icon_path))
        self.save_button.setIconSize(QSize(64, 64))
        
        self.save_button.setStyleSheet(
            """
            QPushButton {
                background-color: #007BFF; /* 科技蓝 */
                color: white; /* 文字颜色为白色 */
                border: none;
                padding: 15px 32px;
                text-align: center;
                text-decoration: none;
                font-size: 16px;
                margin: 4px 2px;
                border: 1px solid #007BFF;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #0062cc; /* 鼠标悬停时的颜色 */
            }
            QPushButton:pressed {
                background-color: #0056b3; /* 按钮被按下时的颜色 */
                border: 1px solid #0056b3; /* 边框颜色与背景一致 */
            }
        """
        )
        
        self.download_button.setStyleSheet(
            """
            QPushButton {
                background-color: #007BFF; /* 科技蓝 */
                color: white; /* 文字颜色为白色 */
                border: none;
                padding: 15px 32px;
                text-align: center;
                text-decoration: none;
                font-size: 16px;
                margin: 4px 2px;
                border: 1px solid #007BFF;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #0062cc; /* 鼠标悬停时的颜色 */
            }
            QPushButton:pressed {
                background-color: #0056b3; /* 按钮被按下时的颜色 */
                border: 1px solid #0056b3; /* 边框颜色与背景一致 */
            }
        """
        )
        self.setStyleSheet(
            """
                QMainWindow {
                    background-color: #A9A9A9; /* 科技浅灰色 */
                }
                QWidget {
                    background-color: #2b2b2b;
                }
                QPushButton {
                    background-color: #007BFF; /* 科技蓝 */
                    border: none;
                    color: white;
                    padding: 15px 32px;
                    text-align: center;
                    text-decoration: none;
                    font-size: 16px;
                    margin: 4px 2px;
                    border: 1px solid #007BFF;
                    border-radius: 4px;
                }
                QPushButton:hover {
                    background-color: #0062cc; /* 鼠标悬停时的颜色 */
                }
                QPushButton:pressed {
                    background-color: #0056b3; /* 按钮被按下时的颜色 */
                    border: 1px solid #0056b3; /* 边框颜色与背景一致 */
                }
                QProgressBar {
                    border: 2px solid #007BFF;
                    border-radius: 5px;
                    text-align: center;
                    color: #007BFF;
                }
                QProgressBar::chunk {
                    background-color: #007BFF;
                    width: 20px;
                }
                QLabel {
                    color: white;
                }
                QLineEdit {
                    background-color: #2b2b2b;
                    color: white;
                    border: 2px solid #007BFF;  /* 科技蓝 */
                    border-radius: 4px;
                }
                QTextEdit {
                    background-color: #2b2b2b;
                    color: white;
                    border: 2px solid #007BFF;  /* 科技蓝 */
                    border-radius: 4px;
                }
                QTableWidget {
                    background-color: #2b2b2b;
                    color: white;
                }
                QTableWidget QHeaderView::section {
                    background-color: #2b2b2b;
                    color: white;
                }
                QComboBox {
                    background-color: #2b2b2b; /* 背景色 */
                    color: white; /* 文字颜色 */
                    border: 2px solid #007BFF; /* 边框颜色 */
                    border-radius: 4px; /* 边框圆角 */
                }
                QComboBox::drop-down {
                    border: none; /* 去掉下拉箭头的边框 */
                }

                QComboBox QAbstractItemView {
                    background-color: #0062cc; /* 下拉选项的背景色 */
                    color: white; /* 下拉选项的文字颜色 */
                }
                QComboBox QAbstractItemView::item:hover {
                    background-color: #0062cc; /* 鼠标悬停时的颜色 */
                }
            """
        )
        
        self.download_thread = None
    
    def load_cookies(self):
        if os.path.exists("cookies.txt"):
            with open("cookies.txt", "r") as f:
                self.cookies_input.setPlainText(f.read())
    def show_error_message(self, message):
        """显示错误消息"""
        QMessageBox.critical(self, "Error", message)
    
    # 保存cookies的方法
    def save_cookies(self):
        cookies = self.cookies_input.toPlainText().strip()
        if cookies:
            with open("cookies.txt", "w") as f:
                f.write(cookies)
            QMessageBox.information(self, "信息", "Cookies已保存。")
            if self.download_thread:
                self.download_thread.set_cookies("cookies.txt")
    def get_download_time(self, file_name):
        # 这里根据实际情况调整，如果是使用下载完成时间，您可能需要设计一个机制来存储这些时间
        # 作为示例，这里使用文件的修改时间作为替代
        return datetime.fromtimestamp(os.path.getmtime(file_name))
    
    # 更新文件表格的方法
    def update_file_table(self):
        """更新文件展示表格，列出当前目录下的视频和音频文件"""
        while self.file_table.rowCount() > 0:
            self.file_table.removeRow(0)
        # 判断当前目录下是否存在视频和音频文件夹 不存在则创建
        if not os.path.exists("视频"):
            os.mkdir("视频")
        if not os.path.exists("音频"):
            os.mkdir("音频")
        
        # 搜索视频和音频文件夹
        folders = ['视频', '音频']
        media_files = []
        for folder in folders:
            folder_path = os.path.join(".", folder)
            if os.path.exists(folder_path):
                files = os.listdir(folder_path)
                media_files.extend([
                    f
                    for f in files
                    if f.lower().endswith((".mp4", ".mkv", ".avi", ".mp3", ".wav"))
                ])
        
        for file in media_files:
            row_position = self.file_table.rowCount()
            self.file_table.insertRow(row_position)
            file_item = QTableWidgetItem(file)
            
            type_indicator = QTableWidgetItem(
                "视频" if file.lower().endswith((".mp4", ".mkv", ".avi")) else "音频"
            )
            self.file_table.setItem(row_position, 0, file_item)
            self.file_table.setItem(row_position, 1, type_indicator)
    
    def update_download_type(self, index):
        # 根据选择的下载类型更新ydl_opts
        download_type = self.download_type.itemText(index)
        
        if self.download_thread:
            self.download_thread.update_format(download_type)
    
    # 更新进度条进度的槽函数
    @pyqtSlot(int)
    def update_progress(self, progress):
        self.progress_bar.setValue(progress)
    
    # 下载完成的槽函数
    @pyqtSlot()
    def download_complete(self):
        self.download_button.setEnabled(False)
        # 判断下载是否成功
        success = self.download_thread.success
        if success:
            self.download_button.setStyleSheet(
                """
                        QPushButton {
                            background-color: #007BFF; /* 恢复原始颜色 */
                            /* 其他样式保持不变 */
                        }
                        QPushButton:hover {
                            background-color: #0062cc;
                        }
                        QPushButton:pressed {
                            background-color: #0056b3;
                        }
                    """
            )
            self.download_button.setText("下载")
        else:
            # 可以在这里处理下载失败的情况
            self.download_button.setText("下载失败.")
            pass
        self.download_thread = None
        
        self.update_file_table()  # 下载完成后更新文件表格
        # 清空url输入框
        self.url_input.clear()
        # 重置进度条
        self.progress_bar.reset()
        # 重新启用下载按钮
        self.download_button.setEnabled(True)
    
    # 下载方法
    def download(self):
        # 检查URL是否为空
        url = self.url_input.text().strip()
        if not url:
            self.show_error_message("请输入有效的视频链接。")
            return
        
        # 如果已有下载线程正在运行，则不执行下载
        if self.download_thread and self.download_thread.isRunning():
            return  # If a download is already running, do nothing
        
        # 获取输入的URL和选择的下载类型
        url = self.url_input.text()
        download_type = self.download_type.currentText()
        
        # 更改按钮文本和样式为"下载中..."
        self.download_button.setText("下载中...")
        self.download_button.setEnabled(False)  # 禁用按钮防止重复点击
        self.download_button.setStyleSheet(
            """
                QPushButton {
                    background-color: #0056b3; /* 模拟按下颜色 */
                    border: none;
                    color: white;
                    padding: 15px 32px;
                    text-align: center;
                    text-decoration: none;
                    font-size: 16px;
                    margin: 4px 2px;
                    border: 1px solid #0056b3; /* 边框颜色与背景一致 */
                    border-radius: 4px;
                }
                QPushButton:hover { /* 由于禁用，此样式不再应用 */
                    background-color: #0062cc;
                }
                QPushButton:pressed { /* 同上 */
                    background-color: #0056b3;
                }
            """
        )
        
        # 创建新的下载线程
        self.download_thread = DownloadThread(url, download_type, '视频', '音频')
        # 连接下载进度和完成信号到相应的槽函数
        self.download_thread.progress.connect(self.update_progress)
        self.download_thread.finished.connect(self.download_complete)
        # 启动下载线程
        self.download_thread.start()
    
    # 双击播放选中文件
    def play_selected_file(self, event):
        row = self.file_table.currentRow()
        file_item = self.file_table.item(row, 0)
        if file_item:
            file_name = file_item.text()
            if file_name.lower().endswith((".mp4", ".mkv", ".avi", ".mp3", ".wav")):
                if sys.platform.startswith("linux"):
                    subprocess.run(["xdg-open", file_name])
                elif sys.platform.startswith("darwin"):
                    subprocess.run(["open", file_name])
                elif sys.platform.startswith("win"):
                    os.startfile(file_name)
    
    # 右键菜单
    def contextMenuEvent(self, event):
        context_menu = QMenu(self)
        context_menu.setStyleSheet(
            """
            QMenu {
                background-color: white; /* 菜单的背景色 */
                color: black; /* 菜单的文字颜色 */
            }
            QMenu::item:selected {
                background-color: lightblue; /* 选中项的背景色 */
            }
        """
        )
        play_action = QAction("播放选中文件", self)
        open_dir_action = QAction("打开文件目录", self)
        context_menu.addAction(play_action)
        context_menu.addAction(open_dir_action)
        action = context_menu.exec_(self.mapToGlobal(event.pos()))
        if action == play_action:
            self.play_selected_file(None)
        elif action == open_dir_action:
            row = self.file_table.currentRow()
            file_item = self.file_table.item(row, 0)
            if file_item:
                file_name = file_item.text()
                if file_name.lower().endswith((".mp4", ".mkv", ".avi", ".mp3", ".wav")):
                    if sys.platform.startswith("linux"):
                        subprocess.run(["xdg-open", file_name])
                    elif sys.platform.startswith("darwin"):
                        subprocess.run(["open", file_name])
                    elif sys.platform.startswith("win"):
                        os.startfile(file_name)