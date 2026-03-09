import sys
import globals
from PyQt6.QtWidgets import QApplication, QMainWindow

from events import Events
from ui.mainwindow import Ui_MainWindow
import events

if __name__ == "__main__":
    app = QApplication(sys.argv)

    globals.window = QMainWindow()
    globals.ui = Ui_MainWindow()
    globals.ui.setupUi(globals.window)

    globals.window.show()

    # codigo a partir aqui

    # Inline events
    globals.ui.txtDNI.editingFinished.connect(
        lambda: Events.check_dni(globals.ui.txtDNI)
    )
    globals.ui.txtMovil.editingFinished.connect(
        lambda: Events.check_tlf(globals.ui.txtMovil)
    )

    sys.exit(app.exec())
