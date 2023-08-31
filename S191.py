import sys
import os
import W508S_to_S191

from PyQt5.QtWidgets import QApplication, QMainWindow, QFileDialog
from PyQt5 import QtWidgets, QtGui
from converter import Ui_MainWindow


class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)
        self.setupUi(self)
        # ico = QtGui.QIcon('cnc.ico')
        # self.setWindowIcon(ico)
        save_data = W508S_to_S191.load_config()
        current_path = save_data[0]
        self.show_path.setText(current_path)

        self.start_button.pressed.connect(
            lambda: self.start_button_pressed(save_data))

        self.read_log_file.triggered.connect(
            lambda: self.read_log_file_pressed())

        self.new_explorer = QFileDialog
        self.change_path.pressed.connect(lambda: self.change_path_pressed())

    def change_path_pressed(self):
        current_path = self.show_path.text()
        dir_name = self.new_explorer.getOpenFileName(
            directory=current_path)
        if not dir_name:
            self.show_path.setText(current_path)
        else:
            self.show_path.setText(dir_name[0])

    def read_log_file_pressed(self):
        mistakes_path = os.path.join(os.path.abspath(''), 'error.log')
        if os.path.exists(mistakes_path):
            os.startfile(mistakes_path)

    def start_button_pressed(self, data):
        current_path = self.show_path.text()
        self.status_label.setText(
            'Выполняется. Ждем...')
        QtWidgets.qApp.processEvents()  # help to show label status
        mistakes = W508S_to_S191.main(current_path, data)
        W508S_to_S191.save_config(current_path)

        if mistakes:
            self.status_label.setText(
                'Что-то пошло не так... Проверьте ошибки в файле error.log программы.')
        else:
            self.status_label.setText(
                'Файл преобразован. Внимательно проверьте каждый кадр.')


app = QApplication(sys.argv)
window = MainWindow()
window.show()
app.exec()
