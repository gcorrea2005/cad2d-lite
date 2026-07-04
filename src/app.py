import sys
from PySide6.QtWidgets import QApplication
from src.view.ui.main_window import MainWindow
from src.view.ui.pug_icon import create_pug_icon


def run():
    app = QApplication(sys.argv)
    app.setApplicationName("DogCAD 2D Lite")
    app.setOrganizationName("DogCad")
    app.setWindowIcon(create_pug_icon())

    window = MainWindow()
    window.show()

    sys.exit(app.exec())
