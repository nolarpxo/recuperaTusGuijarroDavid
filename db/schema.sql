-- PostgreSQL schema for employee/customer management module.

CREATE TABLE IF NOT EXISTS usuarios (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(120) NOT NULL,
    dni VARCHAR(20),
    direccion VARCHAR(255),
    email VARCHAR(160) NOT NULL,
    movil VARCHAR(20),
    tipo VARCHAR(20) NOT NULL CHECK (tipo IN ('cliente', 'empleado'))
);

CREATE TABLE IF NOT EXISTS tareas (
    id SERIAL PRIMARY KEY,
    id_cliente INTEGER NOT NULL REFERENCES usuarios(id) ON DELETE RESTRICT,
    id_empleado INTEGER NOT NULL REFERENCES usuarios(id) ON DELETE RESTRICT,
    servicio VARCHAR(120),
    horas INTEGER NOT NULL DEFAULT 0,
    precio_hora NUMERIC(10, 2) NOT NULL DEFAULT 0,
    estado VARCHAR(30) NOT NULL DEFAULT 'Pendiente'
);
