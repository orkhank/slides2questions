from pathlib import Path
from PyQt5.QtWidgets import *
from py_ui_files.main_window import Ui_MainWindow as MainWindow
from utilities.utils import select_directory_from_pc, show_error_message, give_me_the_dummy_results


class MainPageController(QMainWindow):

    def __init__(self) -> None:
        super().__init__()
        self.page_view = MainWindow()
        self.page_view.setupUi(self)

        self.page_view.pushButton_decrease_subject.clicked.connect(self.decrease_subject_button_clicked)
        self.page_view.pushButton_increase_subject.clicked.connect(self.increase_subject_button_clicked)

        self.page_view.pushButton_decrease_corpus_passes.clicked.connect(self.decrease_corpus_passes_clicked)
        self.page_view.pushButton_increase_corpus_passes.clicked.connect(self.increase_corpus_passes_clicked)

        self.page_view.pushButton_decrease_max_answer_count.clicked.connect(self.decrease_max_answer_count_clicked)
        self.page_view.pushButton_increase_max_answer_count.clicked.connect(self.increase_max_answer_count_clicked)

        self.page_view.pushButton_decrease_min_answer_count.clicked.connect(self.decrease_min_answer_count_clicked)
        self.page_view.pushButton_increase_min_answer_count.clicked.connect(self.increase_min_answer_count_clicked)

        self.page_view.pushButton_decrease_correct_answers.clicked.connect(self.decrease_correct_answers_clicked)
        self.page_view.pushButton_increase_correct_answers.clicked.connect(self.increase_correct_answers_clicked)

        self.page_view.checkBox_extract_from_image.clicked.connect(self.checkBox_extract_from_image_clicked)
        self.page_view.checkBox_verbose.clicked.connect(self.checkBox_verbose_clicked)

        self.page_view.pushButton_directory_select.clicked.connect(self.select_directory)
        self.page_view.pushButton_get_result.clicked.connect(self.get_results)

        self.selected_directory_location = ""
        self.number_of_topics = 0
        self.extract_text_from_images = False
        self.verbose = False
        self.passes_over_corpus = 0
        self.max_answers = 0
        self.min_answers = 0
        self.correct_answers = 0

    def checkBox_verbose_clicked(self, value):
        self.verbose = value
        self.print_parameters()

    def checkBox_extract_from_image_clicked(self, value):
        self.extract_text_from_images = value
        self.print_parameters()

    def increase_correct_answers_clicked(self):
        self.correct_answers += 1
        self.page_view.lineEdit_correct_answers.setText(str(self.correct_answers))
        self.print_parameters()

    def decrease_correct_answers_clicked(self):
        if self.correct_answers == 0:
            show_error_message("Correct Answer Count Hyper Parameter can not be lower than 0")
            self.print_parameters()
            return

        self.correct_answers -= 1
        self.page_view.lineEdit_correct_answers.setText(str(self.correct_answers))
        self.print_parameters()

    def increase_min_answer_count_clicked(self):
        self.min_answers += 1
        self.page_view.lineEdit_min_answer_count.setText(str(self.min_answers))
        self.print_parameters()

    def decrease_min_answer_count_clicked(self):
        if self.min_answers == 0:
            show_error_message("Min Answer Count Hyper Parameter can not be lower than 0")
            self.print_parameters()
            return

        self.min_answers -= 1
        self.page_view.lineEdit_min_answer_count.setText(str(self.min_answers))
        self.print_parameters()

    def increase_max_answer_count_clicked(self):
        self.max_answers += 1
        self.page_view.lineEdit_max_answers_count.setText(str(self.max_answers))
        self.print_parameters()

    def decrease_max_answer_count_clicked(self):
        if self.max_answers == 0:
            show_error_message("Max Answer Count Hyper Parameter can not be lower than 0")
            self.print_parameters()
            return

        self.max_answers -= 1
        self.page_view.lineEdit_max_answers_count.setText(str(self.max_answers))
        self.print_parameters()

    def decrease_corpus_passes_clicked(self):
        if self.passes_over_corpus == 0:
            show_error_message("Passes Over Corpus Hyper Parameter can not be lower than 0")
            self.print_parameters()
            return

        self.passes_over_corpus -= 1
        self.page_view.lineEdit_passes_over_corpus_count.setText(str(self.passes_over_corpus))
        self.print_parameters()

    def increase_corpus_passes_clicked(self):
        self.passes_over_corpus += 1
        self.page_view.lineEdit_passes_over_corpus_count.setText(str(self.passes_over_corpus))
        self.print_parameters()

    def increase_subject_button_clicked(self):
        self.number_of_topics += 1
        self.page_view.lineEdit_topic_count.setText(str(self.number_of_topics))
        self.print_parameters()

    def decrease_subject_button_clicked(self):
        if self.number_of_topics == 0:
            show_error_message("Topic count can not be lower than 0")
            self.print_parameters()
            return

        self.number_of_topics -= 1
        self.page_view.lineEdit_topic_count.setText(str(self.number_of_topics))
        self.print_parameters()

    def select_directory(self):
        directory_location = select_directory_from_pc()

        if directory_location:
            self.selected_directory_location = directory_location
            self.page_view.label_directory.setText(str(self.selected_directory_location))

        self.print_parameters()

    def get_results(self):
        if self.number_of_topics != 0 and self.selected_directory_location != "":
            results = give_me_the_dummy_results()
            self.page_view.plainTextEdit_results.setPlainText(results)
        else:
            show_error_message("you have to check all the parameters")

    def print_parameters(self):
        print("***********************Parameters***********************")
        print(f"Directory location: {self.selected_directory_location}")
        print(f"Number of topics: {self.number_of_topics}")
        print(f"Extract text from topics: {self.extract_text_from_images}")
        print(f"Verbose: {self.verbose}")
        print(f"Passes over corpus: {self.passes_over_corpus}")
        print(f"Max answers: {self.max_answers}")
        print(f"Min answers: {self.min_answers}")
        print(f"Correct answers:{self.correct_answers}")
        print("********************************************************")
