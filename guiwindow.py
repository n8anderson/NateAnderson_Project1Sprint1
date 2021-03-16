from PyQt5.QtWidgets import QMainWindow, QApplication, QWidget, QPushButton, QAction, QLineEdit, QMessageBox, QLabel
from PyQt5.QtWidgets import QVBoxLayout
from PyQt5.QtGui import *
from PyQt5.QtCore import *
import main
import traceback


class Window(QMainWindow):

    def __init__(self, api_url, curs, con):
        super().__init__()
        self.set_file_button = QPushButton('Set File', self)
        self.close_button = QPushButton('Exit', self)
        self.api_button = QPushButton('Populate API Data', self)
        self.textbox = QLineEdit(self)
        self.title = 'Job and School Data'
        self.file_label = QLabel(self)
        self.api_warning = QLabel(self)
        self.api_warning2 = QLabel(self)

        self.file_name = ''
        self.url = api_url
        self.cursor = curs
        self.conn = con
        self.setup_ui()

    def setup_ui(self):
        self.setWindowTitle(self.title)
        self.setGeometry(50, 50, 500, 600)

        self.textbox.move(50, 50)
        self.textbox.resize(120, 20)

        self.set_file_button.move(49, 70)
        self.close_button.move(350, 550)
        self.api_button.move(49, 110)

        self.set_file_button.clicked.connect(self.set_file)
        self.close_button.clicked.connect(self.close_program)
        self.api_button.clicked.connect(self.populate_api)

        self.api_warning.setText('Warning: This will take a long time!')
        self.api_warning2.setText('Gets Data from API website')
        self.api_warning.setGeometry(50, 138, 200, 20)
        self.api_warning2.setGeometry(50, 150, 200, 20)
        self.file_label.setText('Enter File Name:')
        self.file_label.setGeometry(50, 3, 80, 80)
        self.show()

    def populate_api(self):
        try:
            school_data = main.get_data(self.url)
            main.populate_db(self.cursor, school_data)
            main.commit_changes(self.conn)
        except Exception:
            traceback.print_exc()


    def close_program(self):
        main.close_db(self.conn)
        QApplication.instance().quit()

    def set_file(self):
        self.file_name = self.textbox.text()
        try:
            occu_data = main.get_xlsx(self.file_name)
            main.populate_employment(self.cursor, occu_data)
            main.commit_changes(self.conn)
        except FileNotFoundError:
            traceback.print_exc()

