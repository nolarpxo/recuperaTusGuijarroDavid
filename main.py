import sys
import globals
from PyQt6.QtWidgets import QApplication, QMainWindow

from db.connection import init_db
from events import Events, UsuariosController
from ui.mainwindow import Ui_MainWindow

if __name__ == "__main__":
    app = QApplication(sys.argv)

    globals.window = QMainWindow()
    globals.ui = Ui_MainWindow()
    globals.ui.setupUi(globals.window)

    init_db()
    usuarios_controller = UsuariosController(globals.ui)

    globals.window.setStyleSheet(
        """
        QGroupBox { font-weight: 600; }
        QPushButton { min-width: 90px; }
        QTableWidget { gridline-color: #d8d8d8; }
        """
    )

    globals.window.show()

    # codigo a partir aqui

    # Validaciones de formulario
    globals.ui.txtDNI.editingFinished.connect(
        lambda: Events.check_dni(globals.ui.txtDNI)
    )
    globals.ui.txtMovil.editingFinished.connect(
        lambda: Events.check_tlf(globals.ui.txtMovil)
    )
    # CRUD de usuarios
    globals.ui.btnAnadirUsuario.clicked.connect(usuarios_controller.addUsuario)
    globals.ui.btnModificarUsuario.clicked.connect(usuarios_controller.modifUsuario)
    globals.ui.btnEliminarUsuario.clicked.connect(usuarios_controller.delUsuario)
    globals.ui.btnLimpiarUsuario.clicked.connect(usuarios_controller.limpiarFormulario)
    globals.ui.tblUsuarios.itemSelectionChanged.connect(usuarios_controller.selUsuario)
    globals.ui.cmbFiltroTipo.currentIndexChanged.connect(usuarios_controller.cargarUsuario)
    globals.ui.actionSalir.triggered.connect(globals.window.close)

    sys.exit(app.exec())
