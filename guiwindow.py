from PyQt5 import QtCore
from PyQt5.QtWidgets import QMainWindow, QApplication, QTableWidget, QPushButton, QLineEdit, QTableWidgetItem, QLabel
import main


class Window(QMainWindow):

    def __init__(self, api_url, curs, con):
        super().__init__()
        self.set_file_button = QPushButton('Set File', self)
        self.close_button = QPushButton('Exit', self)
        self.api_button = QPushButton('Populate API Data', self)
        self.map_button = QPushButton('Generate Map Data', self)
        self.ascending_order = QPushButton('Sort Ascending', self)
        self.descending_order = QPushButton('Sort Descending', self)
        self.wage_map = QPushButton('Generate Wage Map', self)
        self.jobs_table = QTableWidget(self)
        self.textbox = QLineEdit(self)
        self.title = 'Job and School Data'
        self.file_label = QLabel(self)
        self.api_warning = QLabel(self)
        self.api_warning2 = QLabel(self)
        self.table_instruct = QLabel(self)
        self.sort_by_instruct = QLabel(self)

        self.file_name = ''
        self.url = api_url
        self.cursor = curs
        self.conn = con
        self.setup_ui()

    def setup_ui(self):
        self.setWindowTitle(self.title)
        self.setGeometry(50, 50, 800, 800)
        self.set_jobs_table()
        self.jobs_table.resize(550, 250)
        self.jobs_table.move(50, 200)

        self.textbox.move(50, 50)
        self.textbox.resize(120, 20)

        self.set_file_button.move(49, 70)
        self.close_button.move(350, 550)
        self.api_button.move(49, 110)
        self.map_button.move(49, 170)
        self.ascending_order.move(50, 450)
        self.descending_order.move(150, 450)
        self.wage_map.move(150, 170)

        self.set_file_button.clicked.connect(self.set_file)
        self.close_button.clicked.connect(self.close_program)
        self.api_button.clicked.connect(self.populate_api)
        self.map_button.clicked.connect(self.generate_map)
        self.ascending_order.clicked.connect(self.sort_ascending)
        self.descending_order.clicked.connect(self.sort_descending)
        self.wage_map.clicked.connect(self.gen_wage_map)

        self.api_warning.setText('Warning: This will take a long time!')
        self.api_warning2.setText('Gets Data from API website')
        self.api_warning.setGeometry(50, 138, 200, 20)
        self.api_warning2.setGeometry(50, 150, 200, 20)
        self.file_label.setText('Enter File Name:')
        self.file_label.setGeometry(50, 3, 80, 80)
        self.show()

    def sort_ascending(self):
        self.jobs_table.sortByColumn(2, QtCore.Qt.AscendingOrder)

    def sort_descending(self):
        self.jobs_table.sortByColumn(2, QtCore.Qt.DescendingOrder)

    def gen_wage_map(self):
        main.generate_wage_map(self.conn)

    def generate_map(self):
        main.generate_map(self.conn)

    def set_jobs_table(self):
        salaries = main.get_ratio(main.get_repayment_values(self.conn), main.get_average_salaries(self.conn))
        grads = main.get_ratio(main.get_school_data(self.conn), main.get_employment(self.conn))
        headers = ['State', 'Salaries vs Declining Balance', 'Number of Jobs Per Grad']
        state_list = []
        salaries_list = []
        grads_list = []
        combined_list = []
        for item in salaries['states']:
            state_list.append(item)
        for item in salaries['ratio']:
            salaries_list.append(item)
        for item in grads['ratio']:
            grads_list.append(item)
        for i in range(len(salaries['states'])):
            temp_list = [state_list[i], salaries_list[i], grads_list[i]]
            combined_list.append(temp_list)

        row_count = len(combined_list)
        col_count = len(combined_list[0])

        self.jobs_table.setRowCount(row_count)
        self.jobs_table.setColumnCount(col_count)

        self.jobs_table.setHorizontalHeaderLabels(headers)
        for row in range(row_count):
            for col in range(col_count):
                item = combined_list[row][col]
                self.jobs_table.setItem(row, col, QTableWidgetItem(str(item)))

    def populate_api(self):
        try:
            school_data = main.get_data(self.url)
            main.populate_db(self.cursor, school_data)
            main.commit_changes(self.conn)
            self.set_school_table()
        except FileNotFoundError:
            print('File Not Found')

    def close_program(self):
        main.close_db(self.conn)
        QApplication.instance().quit()

    def set_file(self):
        self.file_name = self.textbox.text()
        try:
            occu_data = main.get_xlsx(self.file_name)
            main.populate_employment(self.cursor, occu_data)
            main.commit_changes(self.conn)
            self.set_jobs_table()
        except FileNotFoundError:
            print('File Not Found')
