from __future__ import annotations

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QAbstractItemView,
    QHeaderView,
    QLineEdit,
    QMessageBox,
    QTableWidgetItem,
)

from services.usuarios_service import UsuarioService


class Events:
    @staticmethod
    def check_dni(widget: QLineEdit) -> bool:
        """
        Valida un DNI/NIF espanol.
        Formato: 8 digitos + 1 letra de control.
        """
        dni = widget.text()

        if not dni:
            widget.setStyleSheet("")
            return False

        dni = dni.upper().strip()

        if len(dni) != 9:
            widget.setStyleSheet("background-color: #B53A22;")
            return False

        letras = "TRWAGMYFPDXBNJZSQVHLCKE"

        try:
            numero = int(dni[:8])
            letra = dni[8]
            letra_correcta = letras[numero % 23]
            is_valid = letra == letra_correcta

            widget.setStyleSheet("background-color: green;" if is_valid else "background-color: #B53A22;")
            return is_valid
        except ValueError:
            widget.setStyleSheet("background-color: #B53A22;")
            return False

    @staticmethod
    def check_tlf(widget: QLineEdit) -> bool:
        """
        Comprueba que el telefono empieza por 6 o 7.
        """
        telefono = widget.text()

        if not telefono:
            widget.setStyleSheet("")
            return False

        is_valid = len(telefono) == 9 and telefono.startswith(("6", "7")) and telefono.isdigit()

        widget.setStyleSheet("background-color: green;" if is_valid else "background-color: #B53A22;")
        return is_valid


class UsuariosController:
    def __init__(self, ui, service: UsuarioService | None = None):
        self.ui = ui
        self.service = service or UsuarioService()
        self.selected_user_id: int | None = None

        self._configure_users_table()
        self.cargarUsuario()

    def addUsuario(self) -> None:
        try:
            usuario = self.service.add_usuario(self._read_form_data())
        except ValueError as exc:
            self._show_error(str(exc))
            return

        self.selected_user_id = usuario.id
        self.cargarUsuario()
        self._select_table_row_by_id(usuario.id)
        self._show_info("Usuario anadido correctamente")

    def delUsuario(self) -> None:
        if self.selected_user_id is None:
            self._show_error("Seleccione un usuario para eliminar")
            return

        result = QMessageBox.question(
            self.ui.tab_usuarios,
            "Confirmar eliminacion",
            "Se eliminara el usuario seleccionado. Continuar?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )

        if result != QMessageBox.StandardButton.Yes:
            return

        try:
            self.service.del_usuario(self.selected_user_id)
        except (LookupError, ValueError) as exc:
            self._show_error(str(exc))
            return

        self.selected_user_id = None
        self.limpiarFormulario()
        self.cargarUsuario()
        self._show_info("Usuario eliminado correctamente")

    def modifUsuario(self) -> None:
        if self.selected_user_id is None:
            self._show_error("Seleccione un usuario para modificar")
            return

        try:
            usuario = self.service.modif_usuario(self.selected_user_id, self._read_form_data())
        except (ValueError, LookupError) as exc:
            self._show_error(str(exc))
            return

        self.selected_user_id = usuario.id
        self.cargarUsuario()
        self._select_table_row_by_id(usuario.id)
        self._show_info("Usuario modificado correctamente")

    def cargarUsuario(self) -> None:
        filtro = self.ui.cmbFiltroTipo.currentText()
        usuarios = self._get_usuarios_filtrados(filtro)

        table = self.ui.tblUsuarios
        table.setRowCount(len(usuarios))

        for row, usuario in enumerate(usuarios):
            values = [
                str(usuario.id),
                usuario.nombre or "",
                usuario.dni or "",
                usuario.direccion or "",
                usuario.email or "",
                usuario.movil or "",
                (usuario.tipo or "").capitalize(),
            ]

            for col, value in enumerate(values):
                item = QTableWidgetItem(value)
                if col == 0:
                    item.setTextAlignment(
                        Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignVCenter
                    )
                table.setItem(row, col, item)

        self._sync_selection_after_reload(usuarios)
        self._update_users_status(filtro, len(usuarios))
        self._refresh_task_combos()

    def selUsuario(self) -> None:
        table = self.ui.tblUsuarios
        selected_items = table.selectedItems()
        if not selected_items:
            return

        row = selected_items[0].row()
        id_item = table.item(row, 0)
        if id_item is None:
            return

        try:
            user_id = int(id_item.text())
        except ValueError:
            return

        usuario = self.service.get_usuario(user_id)
        if usuario is None:
            return

        self.selected_user_id = usuario.id
        self._fill_form_data(usuario)

    def limpiarFormulario(self) -> None:
        self.ui.txtNombre.clear()
        self.ui.txtDNI.clear()
        self.ui.txtDireccion.clear()
        self.ui.txtEmail.clear()
        self.ui.txtMovil.clear()
        self.ui.cmbTipo.setCurrentIndex(0)
        self.ui.tblUsuarios.clearSelection()
        self.selected_user_id = None

    def _configure_users_table(self) -> None:
        table = self.ui.tblUsuarios
        table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        table.verticalHeader().setVisible(False)
        table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)
        table.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeMode.Stretch)
        table.horizontalHeader().setSectionResizeMode(5, QHeaderView.ResizeMode.ResizeToContents)
        table.horizontalHeader().setSectionResizeMode(6, QHeaderView.ResizeMode.ResizeToContents)

    def _read_form_data(self) -> dict[str, str]:
        return {
            "nombre": self.ui.txtNombre.text(),
            "dni": self.ui.txtDNI.text(),
            "direccion": self.ui.txtDireccion.text(),
            "email": self.ui.txtEmail.text(),
            "movil": self.ui.txtMovil.text(),
            "tipo": self.ui.cmbTipo.currentText(),
        }

    def _fill_form_data(self, usuario) -> None:
        self.ui.txtNombre.setText(usuario.nombre or "")
        self.ui.txtDNI.setText(usuario.dni or "")
        self.ui.txtDireccion.setText(usuario.direccion or "")
        self.ui.txtEmail.setText(usuario.email or "")
        self.ui.txtMovil.setText(usuario.movil or "")

        if (usuario.tipo or "").lower() == "cliente":
            self.ui.cmbTipo.setCurrentIndex(1)
        elif (usuario.tipo or "").lower() == "empleado":
            self.ui.cmbTipo.setCurrentIndex(2)
        else:
            self.ui.cmbTipo.setCurrentIndex(0)

    def _refresh_task_combos(self) -> None:
        clientes = self.service.list_usuarios_por_tipo("cliente")
        empleados = self.service.list_usuarios_por_tipo("empleado")

        self._fill_user_combo(
            self.ui.cmbCliente,
            "Seleccione un cliente",
            clientes,
        )
        self._fill_user_combo(
            self.ui.cmbEmpleado,
            "Seleccione un empleado",
            empleados,
        )

    @staticmethod
    def _fill_user_combo(combo, placeholder: str, usuarios) -> None:
        combo.clear()
        combo.addItem(placeholder, None)
        for usuario in usuarios:
            combo.addItem(f"{usuario.id} - {usuario.nombre}", usuario.id)

    def _get_usuarios_filtrados(self, filtro: str):
        filtro_normalizado = (filtro or "").strip().lower()
        if filtro_normalizado in {"cliente", "empleado"}:
            return self.service.list_usuarios_por_tipo(filtro_normalizado)
        return self.service.list_usuarios()

    def _sync_selection_after_reload(self, usuarios) -> None:
        if self.selected_user_id is None:
            return

        if any(usuario.id == self.selected_user_id for usuario in usuarios):
            self._select_table_row_by_id(self.selected_user_id)
            return

        self.limpiarFormulario()

    def _select_table_row_by_id(self, user_id: int) -> bool:
        table = self.ui.tblUsuarios
        for row in range(table.rowCount()):
            item = table.item(row, 0)
            if item is None:
                continue
            if item.text() == str(user_id):
                table.selectRow(row)
                return True
        return False

    def _update_users_status(self, filtro: str, total: int) -> None:
        filtro_normalizado = (filtro or "").strip().lower()
        if filtro_normalizado == "empleado":
            message = f"Mostrando {total} empleado(s) ordenados por nombre"
        elif filtro_normalizado == "cliente":
            message = f"Mostrando {total} cliente(s) ordenados por nombre"
        else:
            message = f"Mostrando {total} usuario(s)"

        self.ui.statusbar.showMessage(message)

    def _show_error(self, text: str) -> None:
        QMessageBox.critical(self.ui.tab_usuarios, "Error", text)

    def _show_info(self, text: str) -> None:
        QMessageBox.information(self.ui.tab_usuarios, "Informacion", text)
