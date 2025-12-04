# 실행 전 install 목록
'''
pip install requests
pip install beautifulsoup4
pip install PyQt6
pip install matplotlib
pip install fpdf2
'''
import sys
from PyQt6.QtWidgets import QApplication
from ui.main_window import MainWindow

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())