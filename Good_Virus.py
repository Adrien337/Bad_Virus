######### Libraries importation

import ctypes
import zipfile
from PySide6.QtCore import Qt, QTimer
from PySide6.QtWidgets import QApplication, QWidget
from PySide6.QtGui import QPainter, QPixmap

########## Configuration
path = "frames.zip"
max_windows = 10
fps = 60

screenWidth = ctypes.windll.user32.GetSystemMetrics(0)
screenHeight = ctypes.windll.user32.GetSystemMetrics(1)


########## Main code


def readZIP(path: str):
    """Return a list of QPixmaps from the ZIP file"""
    frames = []
    with zipfile.ZipFile(path, "r") as zip_ref:
        for name in sorted(zip_ref.namelist()):
            data = zip_ref.read(name)
            pixmap = QPixmap()
            pixmap.loadFromData(data)  # Load JPEG into QPixmap
            frames.append(pixmap)
    return frames


class FrameWindow(QWidget):
    def __init__(self, pixmap, frame_number):
        super().__init__()
        self.pixmap = pixmap
        self.setWindowTitle(f"Frame {frame_number+1:04d}")
        self.resize(screenWidth, screenHeight)
        self.setWindowFlag(Qt.WindowStaysOnTopHint)  # always on top
        self.show()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.drawPixmap(self.rect(), self.pixmap)  # Draw image as background


class BadApple_Player:
    def __init__(self, frames, fps, maxWindows):
        self.frames = frames
        self.fps = fps
        self.max_windows = maxWindows
        self.current_frame = 0
        self.timer = QTimer()
        self.timer.timeout.connect(self.next_frame)
        self.windows = []  # Keep references to avoid garbage collection

    def start(self):
        self.timer.start(int(1000 / self.fps))

    def next_frame(self):
        if self.current_frame >= len(self.frames):
            self.timer.stop()
            return
        win = FrameWindow(self.frames[self.current_frame], self.current_frame)
        self.windows.append(win)
        # Close the oldest window if we exceed max_windows
        if len(self.windows) > self.max_windows:
            old_win = self.windows.pop(0)
            old_win.close()
        self.current_frame += 1


if __name__ == "__main__":
    app = QApplication([])
    frames = readZIP(path)
    player = BadApple_Player(frames, fps, max_windows)
    player.start()
    app.exec()
