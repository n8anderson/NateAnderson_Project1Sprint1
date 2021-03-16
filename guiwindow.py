from PyQt5.QtWidgets import QMainWindow, QApplication, QWidget, QPushButton, QAction, QLineEdit, QMessageBox, QLabel
from PyQt5.QtWidgets import QVBoxLayout
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import pyqtSlot
import main
import traceback


class Window(QMainWindow):

    def __init__(self, curs, con):
        super().__init__()
        self.set_file_button = QPushButton('Set File', self)
        self.close_button = QPushButton('Exit', self)
        self.textbox = QLineEdit(self)
        self.title = 'Job and School Data'
        self.file_label = QLabel()

        self.file_name = ''
        self.cursor = curs
        self.conn = con
        self.setup_ui()

    def setup_ui(self):
        self.setWindowTitle(self.title)
        self.setGeometry(50, 50, 500, 600)

        self.textbox.move(40, 40)
        self.textbox.resize(120, 20)

        self.set_file_button.move(40, 80)
        self.close_button.move(350, 550)

        self.set_file_button.clicked.connect(self.set_file)
        self.close_button.clicked.connect(self.close_program)

        self.file_label.setText('Enter the name of the file here:')
        self.file_label.move(10, 10)
        self.show()
        self.file_label.show()

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

