from __future__ import annotations

from collections.abc import Callable

from sqlalchemy.orm import Session

from db.connection import SessionLocal
from db.models import Tarea, Usuario


class TareaService:
    def __init__(self, session_factory: Callable[[], Session] = SessionLocal):
        self._session_factory = session_factory

    def validar_relaciones_tarea(self, id_cliente: int, id_empleado: int) -> None:
        with self._session_factory() as session:
            cliente = session.get(Usuario, id_cliente)
            empleado = session.get(Usuario, id_empleado)

            if cliente is None:
                raise ValueError("El cliente seleccionado no existe")
            if empleado is None:
                raise ValueError("El empleado seleccionado no existe")
            if cliente.tipo != "cliente":
                raise ValueError("idCliente debe referenciar un usuario de tipo cliente")
            if empleado.tipo != "empleado":
                raise ValueError("idEmpleado debe referenciar un usuario de tipo empleado")

    def guardar_tarea(
        self,
        *,
        id_cliente: int,
        id_empleado: int,
        servicio: str,
        horas: int,
        precio_hora: float,
        estado: str,
    ) -> Tarea:
        self.validar_relaciones_tarea(id_cliente, id_empleado)

        with self._session_factory() as session:
            tarea = Tarea(
                id_cliente=id_cliente,
                id_empleado=id_empleado,
                servicio=servicio,
                horas=horas,
                precio_hora=precio_hora,
                estado=estado,
            )
            session.add(tarea)
            session.commit()
            session.refresh(tarea)
            return tarea
