from PyQt6.QtWidgets import QLineEdit


class Events:
    @staticmethod
    def check_dni(widget: QLineEdit):
        """
        Valida un DNI/NIF español.
        Formato: 8 dígitos + 1 letra de control
        Pone el widget en verde si es correcto
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

            if is_valid:
                widget.setStyleSheet("background-color: green;")
            else:
                widget.setStyleSheet("background-color: #B53A22;")

            return is_valid
        except ValueError:
            widget.setStyleSheet("background-color: #B53A22;")
            return False

    @staticmethod
    def check_tlf(widget: QLineEdit):
        """
        Chequea si el telefono empieza por 6 o 7
        Pone el widget en verde si es correcto, rojo si no
        """
        telefono = widget.text()

        if not telefono:
            widget.setStyleSheet("")
            return False

        is_valid = telefono.startswith("6") or telefono.startswith("7")

        if is_valid:
            widget.setStyleSheet("background-color: green;")
        else:
            widget.setStyleSheet("background-color: #B53A22;")

        return is_valid
