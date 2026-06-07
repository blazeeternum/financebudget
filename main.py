import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from PySide6.QtWidgets import QApplication
from app.database import init_db
from app.ui.main_window import MainWindow
from app.config import BASE_CURRENCY  # loads .env

def main():
    init_db()
    app = QApplication(sys.argv)
    app.setApplicationName("Finance Budget")
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()