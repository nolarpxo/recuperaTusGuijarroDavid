from __future__ import annotations

from collections.abc import Sequence
from datetime import datetime
from pathlib import Path

from PyQt6.QtCore import QRect, Qt
from PyQt6.QtGui import QColor, QFont, QFontMetrics, QPageSize, QPainter, QPdfWriter

from services.usuarios_service import EmpleadoListado


class ReportService:
    def generar_listado_empleados(
        self,
        output_path: str | Path,
        empleados: Sequence[EmpleadoListado],
    ) -> Path:
        if not empleados:
            raise ValueError("No hay empleados para incluir en el informe")

        pdf_path = Path(output_path)
        pdf_path.parent.mkdir(parents=True, exist_ok=True)

        writer = QPdfWriter(str(pdf_path))
        writer.setPageSize(QPageSize(QPageSize.PageSizeId.A4))
        writer.setResolution(96)
        writer.setTitle("LISTADO DE EMPLEADOS")

        painter = QPainter(writer)
        if not painter.isActive():
            raise RuntimeError("No se pudo iniciar la generacion del PDF")

        try:
            self._draw_listado_empleados(writer, painter, empleados)
        finally:
            painter.end()

        return pdf_path

    def _draw_listado_empleados(
        self,
        writer: QPdfWriter,
        painter: QPainter,
        empleados: Sequence[EmpleadoListado],
    ) -> None:
        page_width = writer.width()
        page_height = writer.height()
        margin = 60
        content_width = page_width - (margin * 2)
        bottom_limit = page_height - margin
        generated_at = datetime.now().strftime("%d/%m/%Y %H:%M")

        row_height = 28
        col_widths = [
            int(content_width * 0.30),
            int(content_width * 0.38),
            int(content_width * 0.17),
            content_width - int(content_width * 0.30) - int(content_width * 0.38) - int(content_width * 0.17),
        ]

        current_y = self._draw_page_header(painter, margin, page_width, generated_at)
        current_y = self._draw_table_header(painter, margin, current_y, col_widths, row_height)

        for empleado in empleados:
            if current_y + row_height > bottom_limit:
                writer.newPage()
                current_y = self._draw_page_header(painter, margin, page_width, generated_at)
                current_y = self._draw_table_header(painter, margin, current_y, col_widths, row_height)

            self._draw_employee_row(
                painter,
                empleado,
                margin,
                current_y,
                col_widths,
                row_height,
            )
            current_y += row_height

    def _draw_page_header(
        self,
        painter: QPainter,
        margin: int,
        page_width: int,
        generated_at: str,
    ) -> int:
        painter.setPen(Qt.GlobalColor.black)

        meta_font = QFont("Helvetica", 10)
        painter.setFont(meta_font)
        painter.drawText(
            QRect(margin, margin, page_width - (margin * 2), 20),
            Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter,
            f"Fecha de impresión: {generated_at}",
        )

        title_font = QFont("Helvetica", 16, QFont.Weight.Bold)
        painter.setFont(title_font)
        painter.drawText(
            QRect(margin, margin + 28, page_width - (margin * 2), 30),
            Qt.AlignmentFlag.AlignCenter,
            "LISTADO DE EMPLEADOS",
        )

        painter.drawLine(margin, margin + 68, page_width - margin, margin + 68)
        return margin + 84

    def _draw_table_header(
        self,
        painter: QPainter,
        left: int,
        top: int,
        col_widths: list[int],
        row_height: int,
    ) -> int:
        headers = ["Nombre", "Email", "Móvil", "Tipo"]
        header_font = QFont("Helvetica", 10, QFont.Weight.Bold)
        painter.setFont(header_font)

        current_x = left
        for header, width in zip(headers, col_widths, strict=True):
            rect = QRect(current_x, top, width, row_height)
            painter.fillRect(rect, QColor("#EAEAEA"))
            painter.drawRect(rect)
            self._draw_cell_text(painter, rect, header, bold=True)
            current_x += width

        return top + row_height

    def _draw_employee_row(
        self,
        painter: QPainter,
        empleado: EmpleadoListado,
        left: int,
        top: int,
        col_widths: list[int],
        row_height: int,
    ) -> None:
        values = [
            empleado.nombre,
            empleado.email,
            empleado.movil,
            empleado.tipo,
        ]

        body_font = QFont("Helvetica", 10)
        painter.setFont(body_font)

        current_x = left
        for value, width in zip(values, col_widths, strict=True):
            rect = QRect(current_x, top, width, row_height)
            painter.drawRect(rect)
            self._draw_cell_text(painter, rect, value)
            current_x += width

    @staticmethod
    def _draw_cell_text(
        painter: QPainter,
        rect: QRect,
        text: str,
        *,
        bold: bool = False,
    ) -> None:
        metrics = QFontMetrics(painter.font())
        visible_text = metrics.elidedText(
            text or "",
            Qt.TextElideMode.ElideRight,
            rect.width() - 12,
        )

        if bold:
            font = painter.font()
            font.setBold(True)
            painter.setFont(font)

        painter.drawText(
            rect.adjusted(6, 0, -6, 0),
            Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter,
            visible_text,
        )

        if bold:
            font = painter.font()
            font.setBold(False)
            painter.setFont(font)
