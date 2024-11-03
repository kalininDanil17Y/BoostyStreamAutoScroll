import argparse
import sys

from PyQt5.QtGui import QPalette, QColor
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt

from auto_scroll import AutoScrollApp

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Auto Scroll Boosty Chat App')
    parser.add_argument('--url', type=str, default='https://boosty.to/hellyeahplay/streams/only-chat',
                        help='URL to open in the browser')
    args = parser.parse_args()

    app = QApplication(sys.argv)
    app.setStyle("Fusion")

    # Установливаем темный стиль для приложения
    palette = QPalette()
    palette.setColor(QPalette.Window, QColor(53, 53, 53))
    palette.setColor(QPalette.WindowText, Qt.white)
    palette.setColor(QPalette.Base, QColor(25, 25, 25))
    palette.setColor(QPalette.AlternateBase, QColor(53, 53, 53))
    palette.setColor(QPalette.ToolTipBase, Qt.white)
    palette.setColor(QPalette.ToolTipText, Qt.white)
    palette.setColor(QPalette.Text, Qt.white)
    palette.setColor(QPalette.Button, QColor(53, 53, 53))
    palette.setColor(QPalette.ButtonText, Qt.white)
    palette.setColor(QPalette.BrightText, Qt.red)
    app.setPalette(palette)

    window = AutoScrollApp(args.url)
    window.show()
    sys.exit(app.exec_())