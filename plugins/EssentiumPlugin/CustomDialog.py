from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (QLabel, QDialog, QScrollArea, QVBoxLayout, QDialogButtonBox)


# https://www.pythonguis.com/tutorials/pyqt-dialogs/
class CustomDialog(QDialog):
    def __init__(self, title, message, include_cancel_button=True):
        super().__init__()

        self.setWindowTitle(title)
        if include_cancel_button:
            self.buttonBox = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        else:
            self.buttonBox = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)

        # define scroll area, put message inside of that
        scroll = QScrollArea()
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setWidgetResizable(True)

        # message is a 'QLabel' widget, which is inside a scroll area widget
        scroll.setWidget(QLabel(message))

        # dialog has scrolling message area, then the buttons
        layout = QVBoxLayout()
        layout.addWidget(scroll)
        layout.addWidget(self.buttonBox)
        self.setLayout(layout)

    def show(self):
        return self.exec()
