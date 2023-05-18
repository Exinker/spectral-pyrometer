
import sys

from PySide6 import QtCore, QtGui, QtWidgets

# from core.setting import setdefault_settings
# from core.logging import setdefault_logging


class SettingWidget(QtWidgets.QWidget):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.setFixedWidth(320)


class SpectrumWidget(QtWidgets.QWidget):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.setFixedWidth(640)


class TemperatureWidget(QtWidgets.QWidget):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.setFixedWidth(640)


class CentralWidget(QtWidgets.QWidget):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        layout = QtWidgets.QHBoxLayout(self)
        layout.addWidget(
            SettingWidget(parent=self)
        )
        layout.addWidget(
            SpectrumWidget(parent=self)
        )
        layout.addWidget(
            TemperatureWidget(parent=self)
        )


class MainWindow(QtWidgets.QMainWindow):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # title
        title = f'Spectral Pyrometer - []'
        self.setWindowTitle(title)

        #
        widget = CentralWidget(parent=self)
        self.setCentralWidget(widget)

        #
        self.show()


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()

    sys.exit(app.exec())
