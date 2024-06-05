from PyQt5.QtWidgets import QApplication
from controllers.main_window_controller import MainPageController

app = QApplication([])
window = MainPageController()
window.show()
app.exec_()
