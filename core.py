import os

import yt_dlp
from PyQt5.QtCore import QThread, pyqtSignal


class DownloadThread(QThread):
    # 定义下载进度信号
    progress = pyqtSignal(int)
    # 定义下载完成信号
    finished = pyqtSignal()
    
    # 初始化方法
    def __init__(self, url, download_type, video_output_dir, audio_output_dir):
        super().__init__()
        self.url = url
        self.download_type = download_type
        self.video_output_dir = video_output_dir
        self.audio_output_dir = audio_output_dir
        self.cookies = None
        self.success = False
        self.ydl_opts = {
            "progress_hooks": [self.my_hook],
            "outtmpl": self.get_output_template(download_type),
            "format": (
                "bestaudio/best"
                if self.download_type == "音频"
                else "bestvideo+bestaudio"
            ),
        }
    
    def get_output_template(self, download_type):
        if download_type == "视频":
            return os.path.join(self.video_output_dir, '%(title)s.%(ext)s')
        else:
            return os.path.join(self.audio_output_dir, '%(title)s.%(ext)s')
    
    def update_format(self, download_type):
        if download_type == "视频":
            self.ydl_opts["format"] = "bestvideo+bestaudio"
        else:
            self.ydl_opts["format"] = "bestaudio/best"
        self.ydl_opts["outtmpl"] = self.get_output_template(download_type)
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