from pathlib import Path
from PyQt5.QtWidgets import *
from py_ui_files.main_window import Ui_MainWindow as MainWindow
from utilities.utils import select_directory_from_pc, show_error_message, give_me_the_dummy_results


class MainPageController(QMainWindow):

    def __init__(self) -> None:
        super().__init__()
        self.page_view = MainWindow()
        self.page_view.setupUi(self)

        self.page_view.pushButton_decrease_subject.clicked.connect(self.decrease_button_clicked)
        self.page_view.pushButton_increase_subject.clicked.connect(self.increase_button_clicked)
        self.page_view.pushButton_directory_select.clicked.connect(self.select_directory)
        self.page_view.pushButton_get_result.clicked.connect(self.get_results)

        self.selected_directory_location = ""
        self.topic_count = 0

    def increase_button_clicked(self):
        self.topic_count += 1
        self.page_view.lineEdit_topic_count.setText(str(self.topic_count))

    def decrease_button_clicked(self):
        if self.topic_count == 0:
            show_error_message("Topic count can not be lower than 0")
            return

        self.topic_count -= 1
        self.page_view.lineEdit_topic_count.setText(str(self.topic_count))

    def select_directory(self):
        directory_location = select_directory_from_pc()

        if directory_location:
            self.selected_directory_location = directory_location
            self.page_view.label_directory.setText(self.selected_directory_location)

    def get_results(self):
        if self.topic_count != 0 and self.selected_directory_location != "":
            results = give_me_the_dummy_results()
            self.page_view.plainTextEdit_results.setPlainText(results)
        else:
            show_error_message("you have to check all the parameters")
